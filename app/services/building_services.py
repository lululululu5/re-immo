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
    
with open("app/data/nuts3_to_CDD_HDD.json", "r") as f:
    nuts_hdd_cdd = json.load(f)

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
    