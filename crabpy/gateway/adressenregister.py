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
from crabpy.gateway.exception import GatewayResourceNotFoundException

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

        def gewest_from_json_data(data):
            return Gewest(
                id_=data["id"],
                naam=data["naam"],
                centroid=data["centroid"],
                bounding_box=data["bounding_box"],
                gateway=self,
            )

        def provincie_from_json_data(data):
            return Provincie(
                niscode=data["niscode"],
                naam=data["naam"],
                gewest=data["gewest"],
                gateway=self,
            )

        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        with open(os.path.join(data_dir, "deelgemeenten.json"), encoding="utf-8") as f:
            self.deelgemeenten = json.load(f, object_hook=deelgemeente_from_json_data)
        with open(os.path.join(data_dir, "gewesten.json"), encoding="utf-8") as f:
            self.gewesten = json.load(f, object_hook=gewest_from_json_data)
        with open(os.path.join(data_dir, "provincies.json"), encoding="utf-8") as f:
            self.provincies = json.load(f, object_hook=provincie_from_json_data)

        setup_cache(cache_settings)

    def list_gewesten(self):
        return self.gewesten

    def get_gewest_by_id(self, id_):
        """
        Get a `gewest` by id.

        :param integer id_: The id of a `gewest`.
        :rtype: A :class:`Gewest`.
        """
        for gewest in self.gewesten:
            if gewest.id == id_:
                return gewest
        raise GatewayResourceNotFoundException()

    def list_provincies(self, gewest=2):
        """
        List all `provincies` in a `gewest`.

        :param gewest: The :class:`Gewest` for which the \
            `provincies` are wanted.
        :rtype: A :class:`list` of :class:`Provincie`.
        """
        return [
            provincie for provincie in self.provincies if provincie.gewest == gewest
        ]

    def get_provincie_by_id(self, niscode):
        """
        Retrieve a `provincie` by the niscode.

        :param str niscode: The niscode of the provincie.
        :rtype: :class:`Provincie`
        """
        niscode = str(niscode)
        for provincie in self.provincies:
            if provincie.niscode == niscode:
                return provincie
        return None

    @LONG_CACHE.cache_on_arguments()
    def list_gemeenten_by_provincie(self, provincie):
        """
        List all `gemeenten` in a `provincie`.

        :param provincie: The :class:`Provincie` for which the \
            `gemeenten` are wanted.
        :rtype: A :class:`list` of :class:`Gemeente`.
        """
        if not isinstance(provincie, Provincie):
            provincie = self.get_provincie_by_id(provincie)
        first_niscode_digit = str(provincie.niscode)[0]
        return [
            Gemeente.from_list_response(gemeente, self)
            for gemeente in self.client.get_gemeenten()
            if gemeente["identificator"]["objectId"][0] == first_niscode_digit
        ]

    @LONG_CACHE.cache_on_arguments()
    def list_gemeenten(self, gewest=2):
        """
        List all `gemeenten` in a `gewest`.

        :param gewest: The :class:`Gewest` for which the \
            `gemeenten` are wanted.
        :rtype: A :class:`list` of :class:`Gemeente`.
        """
        first_niscode_digits = [
            provincie.niscode[0]
            for provincie in self.list_provincies(gewest=gewest)
            if provincie.gewest == gewest or gewest is None
        ]
        return [
            Gemeente.from_list_response(gemeente, self)
            for gemeente in self.client.get_gemeenten()
            if gemeente["identificator"]["objectId"][0] in first_niscode_digits
        ]

    @LONG_CACHE.cache_on_arguments()
    def get_gemeente_by_id(self, gemeente_id):
        """
        Retrieve a `gemeente` by the crab id.

        :param integer gemeente_id: The niscode of the gemeente.
        :rtype: :class:`Gemeente`
        """
        return Gemeente.from_get_response(self.client.get_gemeente(gemeente_id), self)

    @LONG_CACHE.cache_on_arguments()
    def get_gemeente_by_niscode(self, niscode):
        """
        Retrieve a `gemeente` by the NIScode.

        :param integer niscode: The NIScode of the gemeente.
        :rtype: :class:`Gemeente`
        """
        return Gemeente.from_get_response(self.client.get_gemeente(niscode), self)

    @LONG_CACHE.cache_on_arguments()
    def list_deelgemeenten(self, gewest=2):
        """
        List all `deelgemeenten` in a `gewest`.

        :param gewest: The :class:`Gewest` for which the \
            `deelgemeenten` are wanted. Currently only Flanders is supported.
        :rtype: A :class:`list` of :class:`Deelgemeente`.
        """
        first_niscode_digits = [
            provincie.niscode[0]
            for provincie in self.list_provincies(gewest=gewest)
            if provincie.gewest == gewest or gewest is None
        ]
        return [
            deelgemeente
            for deelgemeente in self.deelgemeenten
            if deelgemeente.id[0] in first_niscode_digits
        ]

    @LONG_CACHE.cache_on_arguments()
    def list_deelgemeenten_by_gemeente(self, gemeente):
        """
        List all `deelgemeenten` in a `gemeente`.

        :param gemeente: The :class:`Gemeente` for which the \
            `deelgemeenten` are wanted. Currently only Flanders is supported.
        :rtype: A :class:`list` of :class:`Deelgemeente`.
        """
        if not isinstance(gemeente, Gemeente):
            gemeente = self.get_gemeente_by_niscode(gemeente)
        return [
            deelgemeente
            for deelgemeente in self.deelgemeenten
            if deelgemeente.gemeente_niscode == gemeente.niscode
        ]

    @LONG_CACHE.cache_on_arguments()
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
        return [
            Straat.from_list_response(straat, self)
            for straat in self.client.get_straatnamen(gemeentenaam=gemeente.naam)
        ]

    @LONG_CACHE.cache_on_arguments()
    def get_straat_by_id(self, straat_id):
        """
        Retrieve a `straat` by the Id.

        :param integer straat_id: The id of the `straat`.
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
            for adres in self.client.get_adressen(straatnaam=straat.naam)
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


class GatewayObject:

    def __init__(self, gateway):
        self.gateway: Gateway = gateway


class Gewest(GatewayObject):
    """
    A large administrative unit in Belgium.

    Belgium consists of 3 `gewesten`. Together they form the entire territory
    of the country.
    """

    def __init__(self, id_, naam, centroid, bounding_box, gateway=None):
        super().__init__(gateway=gateway)
        self.id = int(id_)
        self.naam = naam
        self.centroid = centroid
        self.bounding_box = bounding_box

    @LazyProperty
    def provincies(self):
        return self.gateway.list_provincies(gewest=self.id)

    @LazyProperty
    def gemeenten(self):
        return self.gateway.list_gemeenten(self.id)

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

    def __init__(self, niscode, naam, gewest, gateway):
        super().__init__(gateway)
        self.niscode = niscode
        self.naam = naam
        self.gewest = gewest

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

    def __init__(self, niscode, gateway, naam=AUTO, taal=AUTO):
        super().__init__(gateway)
        self.niscode = niscode
        if naam is not AUTO:
            self.naam = naam
        if taal is not AUTO:
            self.taal = taal

    @classmethod
    def from_list_response(cls, gemeente, gateway):
        return Gemeente(
            naam=gemeente["gemeentenaam"]["geografischeNaam"]["spelling"],
            niscode=gemeente["identificator"]["objectId"],
            taal=gemeente["gemeentenaam"]["geografischeNaam"]["taal"],
            gateway=gateway,
        )

    @classmethod
    def from_get_response(cls, gemeente, gateway):
        res = Gemeente(niscode=gemeente["identificator"]["objectId"], gateway=gateway)
        res._source_json = gemeente
        return res

    @LazyProperty
    def taal(self):
        taal_nl = False
        taal_fr = False
        for naam in self._source_json["gemeentenamen"]:
            if naam["taal"] == "nl":
                taal_nl = True
            elif naam["taal"] == "fr":
                taal_fr = True
        return "nl" if taal_nl else ("fr" if taal_fr else None)

    @LazyProperty
    def naam(self):
        naam_nl = None
        naam_fr = None
        for naam in self._source_json["gemeentenamen"]:
            if naam["taal"] == "nl":
                naam_nl = naam["spelling"]
            elif naam["taal"] == "fr":
                naam_fr = naam["spelling"]
        return naam_nl or naam_fr

    @LazyProperty
    def straten(self):
        return self.gateway.list_straten(self)

    @LazyProperty
    def provincie(self):
        for p in self.gateway.provincies:
            if self.niscode[0] == p.niscode[0]:
                return p

    @LazyProperty
    @SHORT_CACHE.cache_on_arguments(
        function_key_generator=cache_on_attribute("niscode")
    )
    def _source_json(self):
        return self.gateway.client.get_gemeente(self.niscode)

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
        return Gemeente(niscode=self.gemeente_niscode, gateway=self.gateway)

    def __str__(self):
        return f"{self.naam} ({self.id})"

    def __repr__(self):
        return f"Deelgemeente(id={self.id}"


class Straat(GatewayObject):
    """
    A street.

    A street object is always located in one and exactly one :class:`Gemeente`.
    """

    def __init__(self, id_, gateway, gemeente=AUTO, status=AUTO, naam=AUTO, taal=AUTO):
        super().__init__(gateway)
        self.id = id_
        if naam is not AUTO:
            self.naam = naam
        if taal is not AUTO:
            self.taal = taal
        if status is not AUTO:
            self.status = status
        if gemeente is not AUTO:
            self.gemeente = gemeente

    @classmethod
    def from_list_response(cls, straat, gateway):
        return Straat(
            id_=straat["identificator"]["objectId"],
            taal=straat["straatnaam"]["geografischeNaam"]["taal"],
            status=straat["straatnaamStatus"],
            naam=straat["straatnaam"]["geografischeNaam"]["spelling"],
            gateway=gateway,
        )

    @classmethod
    def from_get_response(cls, straat, gateway):
        res = Straat(id_=straat["identificator"]["objectId"], gateway=gateway)
        res._source_json = straat
        return res

    @LazyProperty
    def taal(self):
        taal_nl = False
        taal_fr = False
        for naam in self._source_json["straatnamen"]:
            if naam["taal"] == "nl":
                taal_nl = True
            elif naam["taal"] == "fr":
                taal_fr = True
        return "nl" if taal_nl else ("fr" if taal_fr else None)

    @LazyProperty
    def naam(self):
        naam_nl = None
        naam_fr = None
        for naam in self._source_json["straatnamen"]:
            if naam["taal"] == "nl":
                naam_nl = naam["spelling"]
            elif naam["taal"] == "fr":
                naam_fr = naam["spelling"]
        return naam_nl or naam_fr

    @LazyProperty
    def status(self):
        return self._source_json["straatnaamStatus"]

    @LazyProperty
    def gemeente(self):
        return Gemeente(
            niscode=self._source_json["gemeente"]["objectId"], gateway=self.gateway
        )

    @LazyProperty
    def adressen(self):
        return self.gateway.list_adressen_by_straat(self)

    @LazyProperty
    @SHORT_CACHE.cache_on_arguments(
        function_key_generator=cache_on_attribute("id")
    )
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
        taal=AUTO,
        gemeente=AUTO,
    ):
        super().__init__(gateway=gateway)
        self.id = id_
        if label is not AUTO:
            self.label = label
        if taal is not AUTO:
            self.taal = taal
        if huisnummer is not AUTO:
            self.huisnummer = huisnummer
        if status is not AUTO:
            self.status = status
        if gemeente is not AUTO:
            self.gemeente = gemeente

    @classmethod
    def from_list_response(cls, adres, gateway):
        return Adres(
            id_=adres["identificator"]["objectId"],
            label=adres["volledigAdres"]["geografischeNaam"]["spelling"],
            taal=adres["volledigAdres"]["geografischeNaam"]["taal"],
            huisnummer=adres["huisnummer"],
            status=adres["adresStatus"],
            gateway=gateway,
        )

    @classmethod
    def from_get_response(cls, adres, gateway):
        res = Adres(id_=adres["identificator"]["objectId"], gateway=gateway)
        res._source_json = adres
        return res

    @LazyProperty
    def label(self):
        return self._source_json["volledigAdres"]["geografischeNaam"]["spelling"]

    @LazyProperty
    def taal(self):
        return self._source_json["volledigAdres"]["geografischeNaam"]["taal"]

    @LazyProperty
    def huisnummer(self):
        return self._source_json["huisnummer"]

    @LazyProperty
    def gemeente(self):
        return Gemeente(
            niscode=self._source_json["gemeente"]["objectId"], gateway=self.gateway
        )

    @LazyProperty
    @SHORT_CACHE.cache_on_arguments(
        function_key_generator=cache_on_attribute("id")
    )
    def _source_json(self):
        return self.gateway.client.get_adres(self.id)

    def __str__(self):
        return f"{self.label} ({self.id})"

    def __repr__(self):
        return f"Adres(id={self.id})"


class Perceel(GatewayObject):
    """A cadastral Parcel."""

    def __init__(self, id_, gateway, status=AUTO):
        super().__init__(gateway=gateway)
        self.id = id_
        if status is not AUTO:
            self.status = status

    @classmethod
    def from_get_response(cls, perceel, gateway):
        res = Perceel(
            id_=perceel["identificator"]["objectId"],
            gateway=gateway,
        )
        res._source_json = perceel
        return res

    @LazyProperty
    @SHORT_CACHE.cache_on_arguments(
        function_key_generator=cache_on_attribute("id")
    )
    def _source_json(self):
        return self.gateway.client.get_perceel(self.id)

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

    def __init__(self, id_, gateway, status=AUTO, percelen=AUTO, geojson=AUTO):
        super().__init__(gateway=gateway)
        self.id = id_
        if status is not AUTO:
            self.status = status
        if percelen is not AUTO:
            self.percelen = percelen
        if geojson is not AUTO:
            self.geojson = geojson

    @classmethod
    def from_get_response(cls, gebouw, gateway):
        res = Gebouw(id_=gebouw["identificator"]["objectId"], gateway=gateway)
        res._source_json = gebouw
        return res

    @LazyProperty
    def status(self):
        return self._source_json["gebouwStatus"]

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
    @SHORT_CACHE.cache_on_arguments(
        function_key_generator=cache_on_attribute("id")
    )
    def _source_json(self):
        return self.gateway.client.get_gebouw(self.id)

    def __str__(self):
        return f"Gebouw {self.id}"

    def __repr__(self):
        return f"Gebouw(id={self.id})"
