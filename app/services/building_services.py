import sqlalchemy as sa
import json
import math

from app.models import Building, Settings
from app import db

from app.data.abatement_factors import abatement_factors, abatement_factors_countries, abatement_factors_property_type

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
    
with open("app/data/share_fossil_fuels_heating.json", "r") as f:
    share_ffuel_heating = json.load(f)
    
with open("app/data/share_electricity_heating_cooling.json", "r") as f:
    share_elec_heating_cooling = json.load(f)
    

class BuildingCalculations:
    
    
    @staticmethod
    def baseline_emissions(building: Building) -> dict:
        """Calculate energy efficiency ratio in comparison with UK"""
        results = {
            "grid_elec": {"emissions": 0},
            "natural_gas": {"emissions": 0},
            "fuel_oil": {"emissions": 0},
            "dist_heating": {"emissions": 0},
            "dist_cooling": {"emissions": 0},
            "o1_energy": {"emissions": 0},
            "o2_energy": {"emissions": 0},
            "f_gas_1": {"emissions": 0},
            "f_gas_2": {"emissions": 0}
        }
        
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
            net_electricity_emissions = electricity_emissions_usage - electricity_emissions_export
            results["grid_elec"] = {"emissions": net_electricity_emissions}
            baseline_emissions += net_electricity_emissions

        if building.natural_gas > 0:
            natural_gas_emissions = building.natural_gas * \
                emission_factors["Gas"]
            results["natural_gas"] = {"emissions": natural_gas_emissions}
            baseline_emissions += natural_gas_emissions

        if building.fuel_oil > 0:
            fuel_oil_emissions = building.fuel_oil * emission_factors["Oil"]
            results["fuel_oil"] = {"emissions": fuel_oil_emissions}
            baseline_emissions += fuel_oil_emissions

        if building.dist_heating > 0:
            district_heating_emissions = building.dist_heating * emission_factors["District Heating"] * electricity_efficiency/electricity_efficiency_uk
            results["dist_heating"] = {"emissions": district_heating_emissions}
            baseline_emissions += district_heating_emissions

        if building.dist_cooling > 0:
            district_cooling_emissions = building.dist_cooling * \
                emission_factors["District Cooling"] * \
                electricity_efficiency/electricity_efficiency_uk
            results["dist_cooling"] = {"emissions": district_cooling_emissions}
            baseline_emissions += district_cooling_emissions

        if building.o1_energy_type is not None and building.o1_consumption > 0:
            o1_emissions = building.o1_consumption * \
                emission_factors[building.o1_energy_type.value]
            results["o1_energy"] = {"emissions":o1_emissions}
            baseline_emissions += o1_emissions

        if building.o2_energy_type is not None and building.o2_consumption > 0:
            o2_emissions = building.o2_consumption * \
                emission_factors[building.o2_energy_type.value]
            results["o2_energy"]= {"emissions": o2_emissions}
            baseline_emissions += o2_emissions

        if building.f_gas_1_type is not None and building.f_gas_1_amount > 0:
            f_gas_1_emissions = building.f_gas_1_amount * \
                emission_factors_coolants[building.f_gas_1_type.value]
            results["f_gas_1"] = {"emissions": f_gas_1_emissions}
            baseline_emissions += f_gas_1_emissions

        if building.f_gas_2_type is not None and building.f_gas_2_amount > 0:
            f_gas_2_emissions = building.f_gas_2_amount * \
                emission_factors_coolants[building.f_gas_2_type.value]
            results["f_gas_2"] = {"emissions":f_gas_2_emissions}
            baseline_emissions += f_gas_2_emissions
            
        results["baseline_emissions"] = baseline_emissions
        
        for key, value in results.items():
            if key != "baseline_emissions":
                share = value["emissions"] / baseline_emissions if baseline_emissions > 0 else 0
                results[key]["share"] = share

        return results
    
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
    
    @staticmethod
    def total_energy_year(building:Building, settings:Settings, year_of_interest) -> float:
        """Total energy required for a year of interest based on growth assumption"""
        elec_procurement_target = BuildingCalculations.total_energy_procurement_year(building, year_of_interest)
        fuel_consumption_target = BuildingCalculations.fuel_consumption(building, settings, year_of_interest)
        dist_heat_cool_target = BuildingCalculations.dist_heating_cooling_year(building, settings, year_of_interest)
        
        return (elec_procurement_target + fuel_consumption_target + dist_heat_cool_target + building.pv_wind_consumed + building.hp_solar_consumed) * settings.reporting_coverage
        
    
    @staticmethod
    def ghg_for_year(building:Building, settings:Settings, year_of_interest, ac_dummy=0) -> float:
        if building.reporting_year > year_of_interest:
            return None
        country_share_elec_heating = share_elec_heating_cooling[building.nuts0]["Heating"]
        country_share_elec_cooling = share_elec_heating_cooling[building.nuts0]["Cooling"]
        country_share_ffuel_heating = share_ffuel_heating[building.nuts0]
        
        baseline_emissions = BuildingCalculations.baseline_emissions(building)
        
        hdd_year_interest = BuildingCalculations.hdd_calculation(building, year_of_interest)
        hdd_2020 = 1  # For now this is hardcoded at, but might change in the future
        hdd_ratio = hdd_year_interest/hdd_2020

        cdd_year_interest = BuildingCalculations.cdd_calculation(building, year_of_interest)
        cdd_2020 = 1  # For now this is hardcoded at, but might change in the future
        cdd_ratio = cdd_year_interest/cdd_2020
        
        if baseline_emissions["baseline_emissions"] == 0:
            return None
        
        else:
            grid_y_reporting = BuildingCalculations.grid_calculation(building, building.reporting_year)
            grid_y_interest = BuildingCalculations.grid_calculation(building, year_of_interest)
            grid_ratio = grid_y_interest/grid_y_reporting

            total_energy_procurement = BuildingCalculations.total_energy_procurement_year(building, building.reporting_year) # For calculations we need to use the first year which is 2020
            energy_ratio = building.grid_elec / total_energy_procurement

        
            electricity_factor = baseline_emissions["grid_elec"]["share"] * ((grid_ratio * energy_ratio + (1-energy_ratio)) * (
                1+country_share_elec_heating * (hdd_year_interest-1) + ac_dummy * country_share_elec_cooling * (cdd_year_interest-1)))
            
            fossils_factor = (baseline_emissions["natural_gas"]["share"] + baseline_emissions["fuel_oil"]["share"] + baseline_emissions["o1_energy"]["share"] + baseline_emissions["o2_energy"]["share"]) * hdd_ratio * (1+country_share_ffuel_heating * (hdd_year_interest - 1))
            
            dist_cooling_factor = baseline_emissions["dist_cooling"]["share"] * cdd_ratio
            
            dist_heating_factor = baseline_emissions["dist_heating"]["share"] * hdd_year_interest * grid_ratio
            
            f_gas_factor = baseline_emissions["f_gas_1"]["share"] + baseline_emissions["f_gas_2"]["share"]

            ghg_emissions_year = baseline_emissions["baseline_emissions"] * \
                (electricity_factor + fossils_factor +
                dist_cooling_factor + dist_heating_factor + f_gas_factor)

            return ghg_emissions_year
    
    @staticmethod
    def building_conversion_factor(building:Building, settings:Settings, year_of_interest) -> float:
        return BuildingCalculations.ghg_for_year(building, settings, year_of_interest)/BuildingCalculations.total_energy_year(building, settings, year_of_interest)
    
    @staticmethod
    def energy_intensity_retrofit(building:Building, settings:Settings, year_of_interest) -> float:
        """The energy_intensity_retrofit function calculates the energy intensity of a building after a retrofit, 
        based on its total energy consumption, size, and various factors such as abatement and depreciation. 
        It returns the maximum target energy intensity achievable given the building's retrofit investment, or zero if no target is achievable."""
        
        energy_consumption = BuildingCalculations.total_energy_year(building, settings, year_of_interest)
        values_surpassed = []

        for target in range(1, 502):
            A = building.size * abatement_factors["mac_f"] / abatement_factors["mac_g"] * \
                abatement_factors_countries[building.nuts0] * \
                abatement_factors_property_type[building.property_type.value]

            B = (math.exp(abatement_factors["mac_g"] * energy_consumption / building.size) -
                math.exp(abatement_factors["mac_g"] * target))

            C = (1 - (abatement_factors["depreciation_a"] *
                    (1 - target / energy_consumption) ** 2 +
                    abatement_factors["depreciation_b"] *
                    (1 - target / energy_consumption) +
                    abatement_factors["depreciation_b"])) ** (year_of_interest - 2015)

            result = A * B * C

            if result >= building.retrofit_investment:
                values_surpassed.append(target)
                

        if len(values_surpassed) > 0:
            return max(values_surpassed)
        else:
            return 0 # Return Net-Zero 
    
        
    @staticmethod
    def energy_consumption_retrofit(building:Building, settings:Settings, year_of_interest) -> float:
        """Depending on the year of interest and the retrofit year we calculate the energy consumption in the case of a retrofit event."""
        if building.size == 0:
            raise ValueError("Non valid Building size. Needs to be bigger than zero")
        
        energy_consumption = BuildingCalculations.total_energy_year(building, settings, year_of_interest)
        if building.retrofit_year:
            energy_intensity_retro = BuildingCalculations.energy_intensity_retrofit(building, settings, building.retrofit_year)
        
        if year_of_interest < building.retrofit_year or building.retrofit_year is None or energy_consumption==0:
            return energy_consumption/building.size
        
        elif year_of_interest == building.retrofit_year:
            return energy_intensity_retro
        
        elif year_of_interest > building.retrofit_year:
            base_year = building.retrofit_year + 2
            energy_ratio = energy_consumption/BuildingCalculations.total_energy_year(building, settings, base_year)
            return energy_intensity_retro * energy_ratio
        
        
    @staticmethod
    def retro_fit_changes(building:Building, settings:Settings, year_of_interest):
        """Calculates Energy and Carbon with respect to retrofit investment"""
        return BuildingCalculations.energy_consumption_retrofit(building, settings, year_of_interest) * BuildingCalculations.building_conversion_factor(building, settings, year_of_interest)
