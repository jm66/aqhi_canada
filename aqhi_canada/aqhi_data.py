import re
import xml.etree.ElementTree as et

from geopy import distance
import requests


class AqhiData(object):
    XML_HOST = "http://dd.weather.gc.ca/"
    XML_LIST_URL = "%s/air_quality/doc/AQHI_XML_File_List.xml" % XML_HOST
    XML_URL_OBS = (
        "%s/air_quality/aqhi/{}/observation/realtime/xml/AQ_OBS_{}_CURRENT.xml"
        % XML_HOST
    )
    XML_URL_FOR = (
        "%s/air_quality/aqhi/{}/forecast/realtime/xml/AQ_FCST_{}_CURRENT.xml"
        % XML_HOST
    )

    conditions_meta = {
        "aqhi": {
            "xpath": "airQualityHealthIndex",
            "english": "Air Quality Health Index",
            "french": "Cote air santé",
        }
    }

    metadata_meta = {
        "timestamp": {"xpath": "dateStamp/UTCStamp"},
        "location": {"xpath": "region"},
    }

    """Get data from Environment Canada."""

    def __init__(
        self,
        province_abr=None,
        region_id=None,
        coordinates=None,
        language="english",
    ):
        """Initialize the data object."""
        if province_abr and region_id:
            self.province_abr = province_abr
            self.region_id = region_id
        else:
            self.closest_region = self.closest_region(
                coordinates[0], coordinates[1]
            )
            self.province_abr = self.closest_region["abreviation"]
            self.region_id = self.closest_region["cgndb"]

        self.language = language
        self.language_abr = language[:2].upper()
        self.metadata = {}
        self.conditions = {}
        self.forecast_time = ""
        self.daily_forecasts = []
        self.hourly_forecasts = []

        self.update()

    def update(self):
        result = requests.get(
            self.XML_URL_OBS.format(self.province_abr, self.region_id),
            timeout=10,
        )
        site_xml = result.content.decode("utf-8-sig")
        xml_object = et.fromstring(site_xml)

        # Update metadata
        for m, meta in self.metadata_meta.items():
            self.metadata[m] = xml_object.find(meta["xpath"]).text

        # Update current conditions
        def get_condition(meta):
            condition = {}

            element = xml_object.find(meta["xpath"])

            if element is not None:
                condition["value"] = element.text
            return condition

        for c, meta in self.conditions_meta.items():
            self.conditions[c] = {"label": meta[self.language]}
            self.conditions[c].update(get_condition(meta))

        # Update forecasts
        result = requests.get(
            self.XML_URL_FOR.format(self.province_abr, self.region_id),
            timeout=10,
        )
        site_xml = result.content.decode("ISO-8859-1")
        xml_object = et.fromstring(site_xml)

        self.forecast_time = xml_object.findtext("./dateStamp/UTCStamp")

        # Update daily forecasts
        period = None
        for f in xml_object.findall("./forecastGroup/forecast"):
            for p in f.findall("./period"):
                if self.language_abr == p.attrib["lang"]:
                    period = p.attrib["forecastName"]
            self.daily_forecasts.append(
                {
                    "period": period,
                    "aqhi": f.findtext("./airQualityHealthIndex"),
                }
            )

        # Update hourly forecasts
        for f in xml_object.findall("./hourlyForecastGroup/hourlyForecast"):
            self.hourly_forecasts.append(
                {"period": f.attrib["UTCTime"], "aqhi": f.text}
            )

    def get_regions(self):
        """Get list of all sites from Environment Canada, for auto-config."""
        result = requests.get(self.XML_LIST_URL, timeout=10)
        site_xml = result.content.decode("utf-8-sig")
        xml_object = et.fromstring(site_xml)

        regions = []
        for zone in xml_object.findall("./EC_administrativeZone"):
            _zone_attrib = zone.attrib
            for region in zone.findall("./regionList/region"):
                _region_attrib = region.attrib
                _children = region.getchildren()
                _region_attrib["latitude"] = float(_region_attrib["latitude"])
                _region_attrib["longitude"] = float(
                    _region_attrib["longitude"]
                )
                for child in _children:
                    _region_attrib[child.tag] = child.text
                _region_attrib.update(_zone_attrib)
                regions.append(_region_attrib)
        return regions

    def closest_region(self, lat, lon):
        """
        Return the region obj with the closest station to our lat/lon."""
        region_list = self.get_regions()

        def site_distance(site):
            """Calculate distance to a region."""
            return distance.distance(
                (lat, lon), (site["latitude"], site["longitude"])
            )

        closest = min(region_list, key=site_distance)

        return closest
