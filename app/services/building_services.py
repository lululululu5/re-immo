import sqlalchemy as sa
import json

from app.models import Building, Settings
from app import db

with open("app/data/energy_efficiency.json", "r") as f:
    eef_data = json.load(f)

with open("app/data/emission_factors_energy.json", "r") as f:
    emission_factors = json.load(f)

with open("app/data/emission_factors_coolants.json", "r") as f:
    emission_factors_coolants = json.load(f)
    
with open("app/data/nuts3_to_CDD_HDD_long.json", "r") as f:
    nuts_hdd_cdd = json.load(f)
    
with open("app/data/share_electricity_heating_cooling.json", "r") as f:
    country_share_heating_cooling = json.load(f)
    
with open(file="app/data/share_fossil_fuels_heating.json") as file:
    share_ffuel_heating = json.load(file)

class BuildingCalculations:
    
    @staticmethod
    def calculate_total_area(building: Building) -> float:
        return building.size * 2
    
    @staticmethod
    def baseline_emissions(building: Building) -> float:
        """Calculate energy efficiency ratio in comparison with UK"""
        electricity_efficiency = eef_data[building.nuts0][str(building.reporting_year)]
        electricity_efficiency_uk = eef_data["UK"][str(building.reporting_year)]
        electricity_efficiency_ratio = electricity_efficiency/electricity_efficiency_uk
        off_site_settings = 1
        
        baseline_emissions = 0
        if building.grid_elec > 0:
            electricity_emissions_usage = (building.grid_elec - (building.off_site_renewables) +
                                           building.off_site_renewables * off_site_settings) * electricity_efficiency
            electricity_emissions_export = building.pv_wind_exported * electricity_efficiency + \
                building.hp_solar_exported * \
                emission_factors["District Heating"] * \
                electricity_efficiency_ratio
            baseline_emissions += electricity_emissions_usage - electricity_emissions_export

        if building.natural_gas > 0:
            natural_gas_emissions = building.natural_gas * \
                emission_factors["Gas"]
            baseline_emissions += natural_gas_emissions

        if building.fuel_oil > 0:
            fuel_oil_emissions = building.fuel_oil * emission_factors["Oil"]
            baseline_emissions += fuel_oil_emissions

        if building.dist_heating > 0:
            district_heating_emissions = building.dist_heating * emission_factors["District Heating"] * electricity_efficiency/electricity_efficiency_uk
            baseline_emissions += district_heating_emissions

        if building.dist_cooling > 0:
            district_cooling_emissions = building.dist_cooling * \
                emission_factors["District Cooling"] * \
                electricity_efficiency/electricity_efficiency_uk
            baseline_emissions += district_cooling_emissions

        if building.o1_energy_type is not None and building.o1_consumption > 0:
            o1_emissions = building.o1_consumption * \
                emission_factors[building.o1_energy_type]
            baseline_emissions += o1_emissions

        if building.o2_energy_type is not None and building.o2_consumption > 0:
            o2_emissions = building.o2_consumption * \
                emission_factors[building.o2_energy_type]
            baseline_emissions += o2_emissions

        if building.f_gas_1_type is not None and building.f_gas_1_amount > 0:
            f_gas_1_emissions = building.f_gas_1_amount * \
                emission_factors_coolants[building.f_gas_1_type]
            baseline_emissions += f_gas_1_emissions

        if building.f_gas_2_type is not None and building.f_gas_2_amount > 0:
            f_gas_2_emissions = building.f_gas_2_amount * \
                emission_factors_coolants[building.f_gas_2_type]
            baseline_emissions += f_gas_2_emissions

        return baseline_emissions
    
    @staticmethod
    def hdd_calculation(building: Building, year_of_interest, settings="low") -> float:
        """
        HDD calculates the heating days required for a future year of interest.
        The formula relies on datapoints that maps the nuts3 Level to hdd projections. There are two scenarios depending on the heat needed 45 and 85
        """
        hdd_2015 = nuts_hdd_cdd[building.nuts3_id]["HDD_2015"]
        index_year = year_of_interest - building.reporting_year + 1
        hdd_factor = nuts_hdd_cdd[building.nuts3_id]["HDD_45_pa"]
        if settings == "high":
            hdd_factor = nuts_hdd_cdd[building.nuts3_id]["HDD_85_pa"]
            
        return (hdd_2015 + index_year * hdd_factor)/ (hdd_2015 + hdd_factor)
    
    @staticmethod
    def cdd_calculation(building: Building, year_of_interest, settings="low") -> float:
        """
        CDD calculates the cooling days required for a future year of interest.
        The formula relies on datapoints that maps the nuts3 Level to cdd projections. There are two scenarios depending on the cooling needed 45 and 85
        """
        cdd_2015 = nuts_hdd_cdd[building.nuts3_id]["CDD_2015"]
        index_year = year_of_interest - building.reporting_year + 1
        cdd_factor = nuts_hdd_cdd[building.nuts3_id]["CDD_45_pa"]
        if settings == "high":
            cdd_factor = nuts_hdd_cdd[building.nuts3_id]["CDD_85_pa"]
            
        return (cdd_2015 + index_year * cdd_factor)/ (cdd_2015 + cdd_factor)
    
    @staticmethod
    def grid_calculation(building: Building, year_of_interest, settings="Default") -> float:
        """Calculates the energy efficiency ratio. Based on projection of efficiencies for various EU countries"""
        if building.reporting_year > year_of_interest:
            return 1
        reporting_year = str(building.reporting_year)
        year_of_interest = str(year_of_interest)
        if settings != "Default":
            return "Custom grid calculation settings are not supported for the time being."
        return eef_data[building.nuts0][year_of_interest] / eef_data[building.nuts0][reporting_year]
    
    @staticmethod
    def total_energy_procurement_year(building: Building, year_of_interest, ac_dummy = 0) -> float:
        """Calculates total energy procurement for a given year. Relies on other static method like hdd and cdd calculation.
        The formula only focuses on elecricity/ energy without heating"""
        base = building.grid_elec
        country_share_elec_heating = country_share_heating_cooling[building.nuts0]["Heating"]
        country_share_elec_cooling = country_share_heating_cooling[building.nuts0]["Cooling"]
        hdd_year_interest = BuildingCalculations.hdd_calculation(building, year_of_interest)
        cdd_year_interest = BuildingCalculations.cdd_calculation(building, year_of_interest)
        total_energy_factor = 1 + country_share_elec_heating * (hdd_year_interest - 1) +\
            ac_dummy * country_share_elec_cooling * (cdd_year_interest - 1)
        total_energy_procurement = (base + building.pv_wind_consumed) * total_energy_factor - building.pv_wind_consumed
        return total_energy_procurement
        

    @staticmethod
    def fuel_consumption(building:Building, settings: Settings, year_of_interest) -> float:
        """Calculate fuel consumption based on projectiond of required heating days"""
        country_share_ffuel_heating = share_ffuel_heating[building.nuts0]
        hdd_year_interest = BuildingCalculations.hdd_calculation(building, year_of_interest)
        factor = 1 + country_share_ffuel_heating * \
            (hdd_year_interest * settings.weather_norm_heat - 1
             )
        usage = (building.natural_gas * settings.natural_gas_coverage +
                 building.fuel_oil * settings.fuel_oil_coverage + building.o1_consumption * settings.o1_coverage + building.o2_consumption * settings.o2_coverage)
        return settings.occupancy_norm * factor * usage * hdd_year_interest * settings.heat_norm
    
    @staticmethod
    def dist_heating_cooling_year(building:Building, settings:Settings, year_of_interest) -> float:
        """Calculate usage of district heating and cooling based on location and required heating and cooling days"""
        hdd_year_interest = BuildingCalculations.hdd_calculation(building, year_of_interest)
        cdd_year_interest = BuildingCalculations.cdd_calculation(building, year_of_interest)
        heating = building.dist_heating * hdd_year_interest * \
            settings.dist_heating_coverage * settings.weather_norm_heat * settings.heat_norm
        cooling = building.dist_cooling * cdd_year_interest * \
            settings.dist_cooling_coverage * settings.weather_norm_cold * settings.cool_norm
        return settings.occupancy_norm * (heating + cooling)

        