"""
This module contains an opionated gateway for the adressen register.

.. versionadded:: 0.14.0
"""
import json
import logging
import os

from dogpile.cache import make_region
from dogpile.util import compat

from crabpy.client import AdressenRegisterClient

LOG = logging.getLogger(__name__)
AUTO = object()

LONG_CACHE = make_region()
SHORT_CACHE = make_region()


def setup_cache(cache_settings):
    if cache_settings is None:
        if not LONG_CACHE.is_configured:
            LONG_CACHE.configure("dogpile.cache.null")
        if not SHORT_CACHE.is_configured:
            SHORT_CACHE.configure("dogpile.cache.null")
    else:
        cache_settings["long.replace_existing_backend"] = True
        LONG_CACHE.configure_from_config(cache_settings, "long.")
        cache_settings["short.replace_existing_backend"] = True
        SHORT_CACHE.configure_from_config(cache_settings, "short.")


def cache_on_attribute(attribute):
    """
    Caches a method and uses an attribtue of the `self` in the caching key.

    Caching bound methods / instance methods without arguments which return
    values dependant on the attributes of the instance can not work with the
    normal `function_key_generator` from dogpile because the generated key
    would be shared across different instances.

    This method returns a `function_key_generator` which will add an
    instance attribute to the key so different instances can store their
    cached data under a different key.
    """

    def function_key_generator(namespace, fn, to_str=str):
        # Copy from dogpile.cache.util except the marked line(s)

        if namespace is None:
            namespace = f"{fn.__module__}:{fn.__name__}"
        else:
            namespace = f"{fn.__module__}:{fn.__name__}|{namespace}"

        fn_args = compat.inspect_getargspec(fn)
        has_self = fn_args[0] and fn_args[0][0] in ("self", "cls")

        def generate_key(*args, **kw):
            if kw:
                raise ValueError(
                    "dogpile.cache's default key creation "
                    "function does not accept keyword arguments."
                )
            if has_self:
                # Start of difference
                args = [args[0].__class__.__name__, getattr(args[0], attribute)] + list(
                    args[1:]
                )
                # End of difference

            return namespace + "|" + " ".join(map(to_str, args))

        return generate_key

    return function_key_generator


class LazyProperty:
    """
    A lazy property is a cached_property which can also be set a value.

    A lazy property will remember the value once it has been accessed once.
    The code inside the property will run maximum 1 time per instance.
    When the property is given a value, the code inside will never run and
    the given value will be returned when retrieving the property.
    """

    def __init__(self, method):
        super().__init__()
        self.method = method
        self.cache_name = f"_cache_{self.method.__name__}"

    def __get__(self, instance, owner):
        try:
            return getattr(instance, self.cache_name)
        except AttributeError:
            value = self.method(instance)
            setattr(instance, self.cache_name, value)
            return value

    def __set__(self, instance, value):
        setattr(instance, self.cache_name, value)


class Gateway:
    """A gateway to the adressen register."""

    def __init__(self, client: AdressenRegisterClient, cache_settings=None):
        self.client = client

        def deelgemeente_from_json_data(data):
            return Deelgemeente(
                id_=data["id"],
                naam=data["naam"],
                gemeente_niscode=data["gemeente_niscode"],
                gateway=self,
            )

        def gemeente_from_json_data(data):
            return Gemeente(
                niscode=data["niscode"],
                provincie_niscode=data["provincie"],
                namen=data["namen"],
                gateway=self,
            )

        def gewest_from_json_data(data):
            return Gewest(
                id_=data["id"],
                naam=data["naam"],
                niscode=data["niscode"],
                centroid=data["centroid"],
                bounding_box=data["bounding_box"],
                gateway=self,
            )

        def provincie_from_json_data(data):
            return Provincie(
                niscode=data["niscode"],
                naam=data["naam"],
                gewest_niscode=data["gewest"],
                gateway=self,
            )

        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        with open(os.path.join(data_dir, "deelgemeenten.json"), encoding="utf-8") as f:
            self.deelgemeenten = json.load(f, object_hook=deelgemeente_from_json_data)
        with open(os.path.join(data_dir, "gewesten.json"), encoding="utf-8") as f:
            self.gewesten = json.load(f, object_hook=gewest_from_json_data)
        with open(os.path.join(data_dir, "provincies.json"), encoding="utf-8") as f:
            self.provincies = json.load(f, object_hook=provincie_from_json_data)
        with open(os.path.join(data_dir, "gemeenten.json"), encoding="utf-8") as f:
            self.gemeenten = [gemeente_from_json_data(data) for data in json.load(f)]

        setup_cache(cache_settings)

    def list_gewesten(self):
        return self.gewesten

    def get_gewest_by_niscode(self, niscode):
        """
        Get a `gewest` by niscode.

        :param string niscode: The niscode of a `gewest`.
        :rtype: A :class:`Gewest`.
        """
        for gewest in self.gewesten:
            if gewest.niscode == niscode:
                return gewest
        return None

    def list_provincies(self, gewest_niscode="2000"):
        """
        List all `provincies` in a `gewest`.

        :param gewest_niscode: The niscode for which the `provincies` are wanted.
        :rtype: A :class:`list` of :class:`Provincie`.
        """
        return [
            provincie
            for provincie in self.provincies
            if provincie.gewest_niscode == gewest_niscode
        ]

    def get_provincie_by_niscode(self, niscode):
        """
        Retrieve a `provincie` by the niscode.

        :param str niscode: The niscode of the provincie.
        :rtype: :class:`Provincie`
        """
        niscode = niscode
        for provincie in self.provincies:
            if provincie.niscode == niscode:
                return provincie
        return None

    def list_gemeenten_by_provincie(self, provincie):
        """
        List all `gemeenten` in a `provincie`.

        :param provincie: The :class:`Provincie` for which the \
            `gemeenten` are wanted.
        :rtype: A :class:`list` of :class:`Gemeente`.
        """
        if not isinstance(provincie, Provincie):
            provincie = self.get_provincie_by_niscode(provincie)
        if provincie is None:
            return []
        provincie_niscode = provincie.niscode
        return [
            gemeente
            for gemeente in self.gemeenten
            if gemeente.provincie_niscode == provincie_niscode
        ]

    def list_gemeenten(self, gewest_niscode="2000"):
        """
        List all `gemeenten` in a `gewest`.

        :param gewest: The :class:`Gewest` for which the \
            `gemeenten` are wanted.
        :rtype: A :class:`list` of :class:`Gemeente`.
        """
        # Brussel is a special case, because it has no provinces
        if gewest_niscode == "4000":
            return [
                gemeente
                for gemeente in self.gemeenten
                if gemeente.niscode.startswith("21")
            ]
        provincie_niscodes = [
            provincie.niscode
            for provincie in self.list_provincies(gewest_niscode=gewest_niscode)
            if provincie.gewest_niscode == gewest_niscode
        ]
        return [
            gemeente
            for gemeente in self.gemeenten
            if gemeente.provincie_niscode in provincie_niscodes
        ]

    def get_gemeente_by_niscode(self, niscode):
        """
        Retrieve a `gemeente` by the NIScode.

        :param string niscode: The NIScode of the gemeente.
        :rtype: :class:`Gemeente`
        """
        return next(
            (gemeente for gemeente in self.gemeenten if gemeente.niscode == niscode),
            None,
        )

    @LONG_CACHE.cache_on_arguments()
    def get_postinfo_by_gemeentenaam(self, gemeente_naam):
        """
        Retrieve a `postinfo` by gemeentenaam.

        :param string gemeente_naam: The name of the municipality.
        :rtype: :class:`Postinfo`
        """
        return [
            Postinfo.from_list_response(postinfo, self)
            for postinfo in self.client.get_postinfos(gemeentenaam=gemeente_naam)
        ]

    @LONG_CACHE.cache_on_arguments()
    def get_postinfo_by_id(self, postcode):
        """
        Retrieve a `postinfo` by crab id.

        :param integer postcode: The postcode the municipality.
        :rtype: :class:`Postinfo`
        """
        return Postinfo.from_get_response(self.client.get_postinfo(postcode), self)

    def list_deelgemeenten(self, gewest_niscode="2000"):
        """
        List all `deelgemeenten` in a `gewest`.

        :param gewest: The :class:`Gewest` for which the \
            `deelgemeenten` are wanted. Currently only Flanders is supported.
        :rtype: A :class:`list` of :class:`Deelgemeente`.
        """
        first_niscode_digits = [
            provincie.niscode[0]
            for provincie in self.list_provincies(gewest_niscode=gewest_niscode)
            if provincie.gewest_niscode == gewest_niscode or gewest_niscode is None
        ]
        return [
            deelgemeente
            for deelgemeente in self.deelgemeenten
            if deelgemeente.id[0] in first_niscode_digits
        ]

    def list_deelgemeenten_by_gemeente(self, gemeente):
        """
        List all `deelgemeenten` in a `gemeente`.

        :param gemeente: The :class:`Gemeente` for which the \
            `deelgemeenten` are wanted. Currently only Flanders is supported.
        :rtype: A :class:`list` of :class:`Deelgemeente`.
        """
        if not isinstance(gemeente, Gemeente):
            gemeente = self.get_gemeente_by_niscode(gemeente)
        if gemeente is None:
            return []
        return [
            deelgemeente
            for deelgemeente in self.deelgemeenten
            if deelgemeente.gemeente_niscode == gemeente.niscode
        ]

    def get_deelgemeente_by_id(self, deelgemeente_id):
        """
        Retrieve a `deelgemeente` by the id.

        :param string deelgemeente_id: The id of the deelgemeente.
        :rtype: :class:`Deelgemeente`
        """
        return next(
            (
                deelgemeente
                for deelgemeente in self.deelgemeenten
                if deelgemeente.id == deelgemeente_id
            ),
            None,
        )

    @LONG_CACHE.cache_on_arguments()
    def list_straten(self, gemeente):
        """
        List all `straten` in a `Gemeente`.

        :param gemeente: The :class:`Gemeente` for which the \
            `straten` are wanted.
        :rtype: A :class:`list` of :class:`Straat`
        """
        if not isinstance(gemeente, Gemeente):
            gemeente = self.get_gemeente_by_niscode(gemeente)
        if gemeente is None:
            return []
        return [
            Straat.from_list_response(straat, self)
            for straat in self.client.get_straatnamen(niscode=gemeente.niscode)
        ]

    @LONG_CACHE.cache_on_arguments()
    def get_straat_by_id(self, straat_id):
        """
        Retrieve a `straat` by the Id.

        :param string straat_id: The id of the `straat`.
        :rtype: :class:`Straat`
        """
        return Straat.from_get_response(self.client.get_straatnaam(straat_id), self)

    @SHORT_CACHE.cache_on_arguments()
    def list_adressen_by_straat(self, straat):
        """
        List all `adressen` in a `Straat`.

        :param straat: The :class:`Straat` for which the \
            `adressen` are wanted.
        :rtype: A :class:`list` of :class:`Adres`
        """
        if not isinstance(straat, Straat):
            straat = self.get_straat_by_id(straat)
        return [
            Adres.from_list_response(adres, self)
            for adres in self.client.get_adressen(straatnaamObjectId=straat.id)
        ]

    @LONG_CACHE.cache_on_arguments()
    def get_adres_by_id(self, adres_id):
        """
        Retrieve a `adres` by the Id.

        :param string adres_id: The id of the `adres`.
        :rtype: :class:`Adres`
        """
        return Adres.from_get_response(self.client.get_adres(adres_id), self)

    @SHORT_CACHE.cache_on_arguments()
    def list_adressen_with_params(
        self,
        gemeentenaam=None,
        postcode=None,
        straatnaam=None,
        homoniem_toevoeging=None,
        huisnummer=None,
        busnummer=None,
        niscode=None,
        status=None,
        straatnaamObjectId=None,
    ):
        """
        List all `adressen` with the given parameters.

        :param gemeentenaam: string
        :param postcode:integer
        :param straatnaam: string
        :param homoniem_toevoeging: string
        :param huisnummer: string
        :param busnummer: string
        :param niscode: string
        :param status: string
        :param straatnaamObjectId: string
        :return: :rtype: Adres
        """
        return [
            Adres.from_list_response(adres, self)
            for adres in self.client.get_adressen(
                gemeentenaam=gemeentenaam,
                postcode=postcode,
                straatnaam=straatnaam,
                homoniem_toevoeging=homoniem_toevoeging,
                huisnummer=huisnummer,
                busnummer=busnummer,
                niscode=niscode,
                status=status,
                straatnaamObjectId=straatnaamObjectId,
            )
        ]

    @SHORT_CACHE.cache_on_arguments()
    def list_percelen_with_params(self, status=None, adresObjectId=None):
        """
        List all `percelen` with the given parameters.

        :param status: str
        :param adresOjbectId: str
        :return: :rtype:
        """

        return [
            Perceel.from_list_response(perceel, self)
            for perceel in self.client.get_percelen(
                status=status, adresObjectId=adresObjectId
            )
        ]

    @SHORT_CACHE.cache_on_arguments()
    def list_adressen_by_perceel(self, perceel):
        """
        List all `adressen` in a `Perceel`.

        :param perceel: The :class:`Perceel` for which the \
            `adressen` are wanted.
        :rtype: A :class:`list` of :class:`Adres`
        """
        if not isinstance(perceel, Perceel):
            perceel = self.get_perceel_by_id(perceel)
        return perceel.adressen

    @SHORT_CACHE.cache_on_arguments()
    def get_perceel_by_id(self, perceel_id):
        """
        Retrieve a `Perceel` by the Id.

        :param string perceel_id: the Id of the `Perceel`
        :rtype: :class:`Perceel`
        """
        return Perceel.from_get_response(self.client.get_perceel(perceel_id), self)

    @SHORT_CACHE.cache_on_arguments()
    def get_gebouw_by_id(self, gebouw_id):
        """
        Retrieve a `Gebouw` by the Id.

        :param str gebouw_id: the Id of the `Gebouw`
        :rtype: :class:`Gebouw`
        """
        return Gebouw.from_get_response(self.client.get_gebouw(gebouw_id), self)


class CallableString(str):
    def __call__(self, *args, **kwargs):
        return self


class GatewayObject:
    def __init__(self, gateway):
        self.gateway: Gateway = gateway


class Gewest(GatewayObject):
    """
    A large administrative unit in Belgium.

    Belgium consists of 3 `gewesten`. Together they form the entire territory
    of the country.
    """

    def __init__(self, id_, niscode, naam, centroid, bounding_box, gateway=None):
        super().__init__(gateway=gateway)
        self.id = int(id_)
        self.naam = naam
        self.niscode = niscode
        self.centroid = centroid
        self.bounding_box = bounding_box

    @LazyProperty
    def provincies(self):
        return self.gateway.list_provincies(gewest_niscode=self.niscode)

    @LazyProperty
    def gemeenten(self):
        return self.gateway.list_gemeenten(self.niscode)

    def __str__(self):
        if self.naam is not None:
            return f"{self.naam} ({self.id})"
        else:
            return f"Gewest {self.id}"

    def __repr__(self):
        return f"Gewest(id={self.id})"


class Provincie(GatewayObject):
    """
    The largest administrative unit within a :class:`Gewest`.

    .. versionadded:: 0.4.0
    """

    def __init__(self, niscode, naam, gewest_niscode, gateway):
        super().__init__(gateway)
        self.niscode = niscode
        self.naam = naam
        self.gewest_niscode = gewest_niscode

    @LazyProperty
    def gemeenten(self):
        return self.gateway.list_gemeenten_by_provincie(self)

    def __str__(self):
        return f"{self.naam} ({self.niscode})"

    def __repr__(self):
        return f"Provincie(niscode={self.niscode})"


class Gemeente(GatewayObject):
    """
    The smallest administrative unit in Belgium.
    """

    def __init__(self, niscode, gateway, provincie_niscode=None, namen=None, naam=None):
        super().__init__(gateway)
        self.niscode = niscode
        self.provincie_niscode = provincie_niscode
        if not (namen or naam):
            raise ValueError("Either namen or naam must be given")
        if namen is not None:
            self.namen = namen
        if naam is not None:
            if isinstance(naam, str):
                naam = CallableString(naam)
            if not callable(naam):
                raise ValueError("naam must be a callable")
            self.naam = naam

    def naam(self, taal="nl"):
        return next(
            (naam["naam"] for naam in self.namen if naam["taal"] == taal),
            self.namen[0]["naam"],
        )

    @LazyProperty
    def straten(self):
        return self.gateway.list_straten(self)

    @LazyProperty
    def postinfo(self):
        gemeente_naam = self.naam() if not isinstance(self.naam, str) else self.naam
        return self.gateway.get_postinfo_by_gemeentenaam(gemeente_naam)

    @LazyProperty
    def provincie(self):
        return self.gateway.get_provincie_by_niscode(self.provincie_niscode)

    @LazyProperty
    def gewest(self):
        return self.gateway.get_gewest_by_niscode(self.provincie.gewest_niscode)

    def __str__(self):
        return f"{self.naam} ({self.niscode})"

    def __repr__(self):
        return f"Gemeente(niscode={self.niscode})"


class Deelgemeente(GatewayObject):
    """
    A subdivision of a :class:`Gemeente`.

    .. versionadded:: 0.7.0
    """

    def __init__(self, id_, naam, gemeente_niscode, gateway):
        super().__init__(gateway)
        self.id = id_
        self.naam = naam
        self.gemeente_niscode = gemeente_niscode

    @LazyProperty
    def gemeente(self):
        return self.gateway.get_gemeente_by_niscode(self.gemeente_niscode)

    def __str__(self):
        return f"{self.naam} ({self.id})"

    def __repr__(self):
        return f"Deelgemeente(id={self.id}"


class Straat(GatewayObject):
    """
    A street.

    A street object is always located in one and exactly one :class:`Gemeente`.
    """

    def __init__(self, id_, gateway, gemeente=AUTO, status=AUTO, naam=AUTO, uri=AUTO):
        super().__init__(gateway)
        self.id = id_
        if naam is not AUTO:
            if isinstance(naam, str):
                naam = CallableString(naam)
            if not callable(naam):
                raise ValueError("naam must be a callable")
            self.naam = naam
        if status is not AUTO:
            self.status = status
        if gemeente is not AUTO:
            self.gemeente = gemeente
        if uri is not AUTO:
            self.uri = uri

    @classmethod
    def from_list_response(cls, straat, gateway):
        return Straat(
            id_=straat["identificator"]["objectId"],
            status=straat["straatnaamStatus"],
            naam=straat["straatnaam"]["geografischeNaam"]["spelling"],
            uri=straat["identificator"]["id"],
            gateway=gateway,
        )

    @classmethod
    def from_get_response(cls, straat, gateway):
        res = Straat(id_=straat["identificator"]["objectId"], gateway=gateway)
        res._source_json = straat
        return res

    def naam(self, taal="nl"):
        naam = next(
            (
                straatnaam["spelling"]
                for straatnaam in self._source_json["straatnamen"]
                if straatnaam["taal"] == taal
            ),
            None,
        )
        if naam:
            return naam

        return self._source_json["straatnamen"][0]["spelling"]

    @LazyProperty
    def uri(self):
        return self._source_json["identificator"]["id"]

    @LazyProperty
    def status(self):
        return self._source_json["straatnaamStatus"]

    @LazyProperty
    def gemeente(self):
        gemeente_niscode = self._source_json["gemeente"]["objectId"]
        return self.gateway.get_gemeente_by_niscode(gemeente_niscode)

    @LazyProperty
    def adressen(self):
        return self.gateway.list_adressen_by_straat(self)

    @LazyProperty
    @SHORT_CACHE.cache_on_arguments(function_key_generator=cache_on_attribute("id"))
    def _source_json(self):
        return self.gateway.client.get_straatnaam(self.id)

    def __str__(self):
        return f"{self.naam} ({self.id})"

    def __repr__(self):
        return f"Straat(id={self.id})"


class Adres(GatewayObject):
    """
    An address.

    An address object is always located in one and exactly one :class:`Gemeente`.
    """

    def __init__(
        self,
        id_,
        gateway,
        status=AUTO,
        huisnummer=AUTO,
        label=AUTO,
        gemeente=AUTO,
        straat=AUTO,
        postinfo=AUTO,
        busnummer=AUTO,
        uri=AUTO,
    ):
        super().__init__(gateway=gateway)
        self.id = id_
        if label is not AUTO:
            self.label = label
        if huisnummer is not AUTO:
            self.huisnummer = huisnummer
        if status is not AUTO:
            self.status = status
        if gemeente is not AUTO:
            self.gemeente = gemeente
        if straat is not AUTO:
            self.straat = straat
        if postinfo is not AUTO:
            self.postinfo = postinfo
        if busnummer is not AUTO:
            self.busnummer = busnummer
        if status is not AUTO:
            self.status = status
        if uri is not AUTO:
            self.uri = uri

    @classmethod
    def from_list_response(cls, adres, gateway):
        return Adres(
            id_=adres["identificator"]["objectId"],
            label=adres["volledigAdres"]["geografischeNaam"]["spelling"],
            huisnummer=adres["huisnummer"],
            busnummer=adres.get("busnummer", ""),
            status=adres["adresStatus"],
            uri=adres["identificator"]["id"],
            gateway=gateway,
        )

    @classmethod
    def from_get_response(cls, adres, gateway):
        res = Adres(id_=adres["identificator"]["objectId"], gateway=gateway)
        res._source_json = adres
        return res

    @LazyProperty
    def uri(self):
        return self._source_json["identificator"]["id"]

    @LazyProperty
    def label(self):
        return self._source_json["volledigAdres"]["geografischeNaam"]["spelling"]

    @LazyProperty
    def huisnummer(self):
        return self._source_json["huisnummer"]

    @LazyProperty
    def status(self):
        return self._source_json["adresStatus"]

    @LazyProperty
    def straat(self):
        return Straat(
            id_=self._source_json["straatnaam"]["objectId"],
            naam=self._source_json["straatnaam"]["straatnaam"]["geografischeNaam"][
                "spelling"
            ],
            gateway=self.gateway,
        )

    @LazyProperty
    def postinfo(self):
        return Postinfo(
            id_=self._source_json["postinfo"]["objectId"],
            gateway=self.gateway,
        )

    @LazyProperty
    def busnummer(self):
        return self._source_json.get("busnummer", "")

    @LazyProperty
    def gemeente(self):
        gemeente_niscode = self._source_json["gemeente"]["objectId"]
        return self.gateway.get_gemeente_by_niscode(gemeente_niscode)

    @LazyProperty
    @SHORT_CACHE.cache_on_arguments(function_key_generator=cache_on_attribute("id"))
    def _source_json(self):
        return self.gateway.client.get_adres(self.id)

    def __str__(self):
        return f"{self.label} ({self.id})"

    def __repr__(self):
        return f"Adres(id={self.id})"


class Perceel(GatewayObject):
    """A cadastral Parcel."""

    def __init__(self, id_, gateway, status=AUTO, uri=AUTO):
        super().__init__(gateway=gateway)
        self.id = id_
        if status is not AUTO:
            self.status = status
        if uri is not AUTO:
            self.uri = uri

    @classmethod
    def from_list_response(cls, perceel, gateway):
        return Perceel(
            id_=perceel["identificator"]["objectId"],
            status=perceel["perceelStatus"],
            uri=perceel["identificator"]["id"],
            gateway=gateway,
        )

    @classmethod
    def from_get_response(cls, perceel, gateway):
        res = Perceel(
            id_=perceel["identificator"]["objectId"],
            gateway=gateway,
        )
        res._source_json = perceel
        return res

    @LazyProperty
    @SHORT_CACHE.cache_on_arguments(function_key_generator=cache_on_attribute("id"))
    def _source_json(self):
        return self.gateway.client.get_perceel(self.id)

    @LazyProperty
    def uri(self):
        return self._source_json["identificator"]["id"]

    @LazyProperty
    def status(self):
        return self._source_json["perceelStatus"]

    @LazyProperty
    def adressen(self):
        return [
            Adres(id_=adres["objectId"], gateway=self.gateway)
            for adres in self._source_json["adressen"]
        ]

    def __str__(self):
        return f"Perceel {self.id}"

    def __repr__(self):
        return f"Perceel(id={self.id})"


class Gebouw(GatewayObject):
    """
    A building.
    """

    def __init__(self, id_, gateway, status=AUTO, percelen=AUTO, geojson=AUTO, uri=AUTO):
        super().__init__(gateway=gateway)
        self.id = id_
        if status is not AUTO:
            self.status = status
        if percelen is not AUTO:
            self.percelen = percelen
        if geojson is not AUTO:
            self.geojson = geojson
        if uri is not AUTO:
            self.uri = uri

    @classmethod
    def from_get_response(cls, gebouw, gateway):
        res = Gebouw(id_=gebouw["identificator"]["objectId"], gateway=gateway)
        res._source_json = gebouw
        return res

    @LazyProperty
    def status(self):
        return self._source_json["gebouwStatus"]

    @LazyProperty
    def uri(self):
        return self._source_json["identificator"]["id"]

    @LazyProperty
    def percelen(self):
        return [
            Perceel(id_=perceel["objectId"], gateway=self.gateway)
            for perceel in self._source_json["percelen"]
        ]

    @LazyProperty
    def geojson(self):
        return self._source_json["geometriePolygoon"]

    @LazyProperty
    @SHORT_CACHE.cache_on_arguments(function_key_generator=cache_on_attribute("id"))
    def _source_json(self):
        return self.gateway.client.get_gebouw(self.id)

    def __str__(self):
        return f"Gebouw {self.id}"

    def __repr__(self):
        return f"Gebouw(id={self.id})"


class Postinfo(GatewayObject):
    """
    Postal code information.
    """

    def __init__(self, id_, gateway, namen=AUTO, status=AUTO, gemeente=AUTO, uri=AUTO):
        super().__init__(gateway=gateway)
        self.id = id_
        if status is not AUTO:
            self.status = status
        if namen is not AUTO:
            if callable(namen):
                self.namen = namen
            else:
                raise ValueError("namen must be callable")
        if gemeente is not AUTO:
            self.gemeente = gemeente
        if uri is not AUTO:
            self.uri = uri

    @classmethod
    def from_list_response(cls, postinfo, gateway):
        return Postinfo(
            id_=postinfo["identificator"]["objectId"],
            status=postinfo["postInfoStatus"],
            uri=postinfo["identificator"]["id"],
            gateway=gateway,
        )

    @classmethod
    def from_get_response(cls, postinfo, gateway):
        res = Postinfo(id_=postinfo["identificator"]["objectId"], gateway=gateway)
        res._source_json = postinfo
        return res

    @LazyProperty
    def uri(self):
        return self._source_json["identificator"]["id"]

    @LazyProperty
    def status(self):
        return self._source_json["postInfoStatus"]

    @LazyProperty
    def gemeente(self):
        niscode = self._source_json["gemeente"]["objectId"]
        return self.gateway.get_gemeente_by_niscode(niscode)

    def namen(self, taal="nl"):
        namen = [
            postnaam["geografischeNaam"]["spelling"]
            for postnaam in self._source_json["postnamen"]
            if postnaam["geografischeNaam"]["taal"] == taal
        ]
        if namen:
            return namen
        else:
            return [
                postnaam["geografischeNaam"]["spelling"]
                for postnaam in self._source_json["postnamen"]
            ]

    @LazyProperty
    @SHORT_CACHE.cache_on_arguments(function_key_generator=cache_on_attribute("id"))
    def _source_json(self):
        return self.gateway.client.get_postinfo(self.id)

    def __str__(self):
        return f"Postinfo {self.id}"

    def __repr__(self):
        return f"Postinfo(id={self.id})"
