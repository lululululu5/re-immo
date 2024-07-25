import unittest
from app import create_app, db
from app.models import User, Building, Settings
from app.services.building_services import BuildingCalculations
from config import Config

class TestConfig(Config):
    Testing=True
    SQLALCHEMY_DATABASE_URI = "sqlite://"

class UserModelCase(unittest.TestCase):
    def setUp(self): 
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_password_hashing(self):
        u = User(name="susan", email="susan@mail.com")
        u.set_password("cat")
        self.assertFalse(u.check_password("dog"))
        self.assertTrue(u.check_password("cat"))
        
    
class BuildingModelCase(unittest.TestCase):
    def setUp(self): 
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create a user
        self.user = User(name="Test", email="test@email.com")
        self.user.set_password("test")
        db.session.add(self.user)
        db.session.commit()
        
        # Create buildings
        self.building_good = Building(address="Proski 100", reporting_year=2020,  country="DE", zip="10247", property_type="RMF", size=1000, grid_elec=1000, fuel_oil=2000, dist_heating=1000, dist_cooling=5000, retrofit_year=2035, retrofit_investment=100000, user_id=self.user.id)
        self.building_bad = Building(address="Hauptstrasse 1", reporting_year=2023,  country="DE", zip="30161", property_type="RMF", size=1000, grid_elec=44600, natural_gas=50000, fuel_oil=6000, dist_heating=74600, dist_cooling=2500, o1_energy_type="biogas", o1_consumption=10000, o2_energy_type="wood_pellets", o2_consumption=1000, f_gas_1_type="METHANE_CH4", f_gas_1_amount=100, pv_wind_consumed=5000, pv_wind_exported=10000, hp_solar_consumed=2500, hp_solar_exported=5000, retrofit_year=2030, retrofit_investment=100000, user_id=self.user.id)
        db.session.add(self.building_good)
        db.session.add(self.building_bad)
        db.session.commit()
        
        #Create settings
        self.settings_good = Settings(building_id=self.building_good.id)
        self.settings_bad = Settings(building_id=self.building_bad.id)
        db.session.add(self.settings_good)
        db.session.add(self.settings_bad)
        db.session.commit()
        
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    
    
    def test_baseline_emissions(self):
        emissions_good = BuildingCalculations.baseline_emissions(self.building_good)
        emissions_bad = BuildingCalculations.baseline_emissions(self.building_bad)
        self.assertEqual(round(emissions_good["baseline_emissions"],2), 2612.89)
        self.assertEqual(round(emissions_bad["baseline_emissions"],2), 58379.24)
    
    def test_hdd_calculation(self):
        hdd_good = BuildingCalculations.hdd_calculation(self.building_good, 2030)
        hdd_bad = BuildingCalculations.hdd_calculation(self.building_bad, 2030)
        self.assertEqual(round(hdd_good, 5), 0.97843)
        self.assertEqual(round(hdd_bad, 5), 0.98457)
    
    def test_cdd_calculation(self):
        cdd_good = BuildingCalculations.cdd_calculation(self.building_good, 2030)
        cdd_bad = BuildingCalculations.cdd_calculation(self.building_bad, 2030)
        self.assertEqual(round(cdd_good, 5), 1.09974)
        self.assertEqual(round(cdd_bad, 5), 1.07852)
    
    def test_grid_calculation(self):
        grid_good = BuildingCalculations.grid_calculation(self.building_good, 2030)
        grid_bad = BuildingCalculations.grid_calculation(self.building_bad, 2030)
        self.assertEqual(round(grid_good, 5), 0.66655)
        self.assertEqual(round(grid_bad, 5), 0.60861)
    
    def test_total_energy_procurement_year(self):
        energy_procurement_good = BuildingCalculations.total_energy_procurement_year(self.building_good, 2030)
        energy_procurement_bad = BuildingCalculations.total_energy_procurement_year(self.building_bad, 2030)
        self.assertEqual(round(energy_procurement_good, 2), 999.22)
        self.assertEqual(round(energy_procurement_bad, 2), 44572.15)
    
    def test_fuel_consumption(self):
        fuel_consumption_good = BuildingCalculations.fuel_consumption(self.building_good, self.settings_good, 2030)
        fuel_consumption_bad = BuildingCalculations.fuel_consumption(self.building_bad, self.settings_bad, 2030)
        self.assertEqual(round(fuel_consumption_good, 2), 1924.24)
        self.assertEqual(round(fuel_consumption_bad, 2), 65178.82)
    
    def test_dist_heating_cooling_year(self):
        dist_hc_consumption_good = BuildingCalculations.dist_heating_cooling_year(self.building_good, self.settings_good, 2030)
        dist_hc_consumption_bad = BuildingCalculations.dist_heating_cooling_year(self.building_bad, self.settings_bad, 2030)
        self.assertEqual(round(dist_hc_consumption_good, 2), 6477.13)
        self.assertEqual(round(dist_hc_consumption_bad, 2), 76144.86)
    
    def test_total_energy_year(self):
        total_energy_good = BuildingCalculations.total_energy_year(self.building_good, self.settings_good, 2030)
        total_energy_bad = BuildingCalculations.total_energy_year(self.building_bad, self.settings_bad, 2030)
        self.assertEqual(round(total_energy_good, 2), 9400.58)
        self.assertEqual(round(total_energy_bad, 2), 193395.83)
    
    def test_ghg_for_year(self):
        ghg_year_good = BuildingCalculations.ghg_for_year(self.building_good, self.settings_good, 2030)
        ghg_year_bad = BuildingCalculations.ghg_for_year(self.building_bad, self.settings_bad, 2030)
        self.assertEqual(round(ghg_year_good, 2), 2525.87)
        self.assertEqual(round(ghg_year_bad, 2), 41066.45)
    
    def test_building_conversion_factor(self):
        conversion_f_good = BuildingCalculations.building_conversion_factor(self.building_good, self.settings_good, 2030)
        conversion_f_bad = BuildingCalculations.building_conversion_factor(self.building_bad, self.settings_bad, 2030)
        self.assertEqual(round(conversion_f_good, 5), 0.26869)
        self.assertEqual(round(conversion_f_bad, 5), 0.21234)
    
    def test_energy_consumption_retrofit(self):
        conversion_f_good_2025 = BuildingCalculations.energy_consumption_retrofit(self.building_good, self.settings_good, 2025)
        conversion_f_good_2035 = BuildingCalculations.energy_consumption_retrofit(self.building_good, self.settings_good, 2035)
        conversion_f_bad_2025 = BuildingCalculations.energy_consumption_retrofit(self.building_bad, self.settings_bad, 2025)
        conversion_f_bad_2030 = BuildingCalculations.energy_consumption_retrofit(self.building_bad, self.settings_bad, 2030)
        conversion_f_bad_2035 = BuildingCalculations.energy_consumption_retrofit(self.building_bad, self.settings_bad, 2035)
        self.assertEqual(round(conversion_f_good_2025, 4), 9.2001)
        self.assertEqual(round(conversion_f_good_2035, 0), 0)
        self.assertEqual(round(conversion_f_bad_2025, 4), 195.3963)
        self.assertEqual(round(conversion_f_bad_2030, 0), 58)
        self.assertEqual(round(conversion_f_bad_2035, 4), 57.6413)
        
    
    def test_retro_fit_changes(self):
        retro_fit_changes_good_2034 = BuildingCalculations.retro_fit_changes(self.building_good, self.settings_good, 2034)
        retro_fit_changes_good_2035 = BuildingCalculations.retro_fit_changes(self.building_good, self.settings_good, 2035)
        retro_fit_changes_bad_2029 = BuildingCalculations.retro_fit_changes(self.building_bad, self.settings_bad, 2029)
        retro_fit_changes_bad_2030 = BuildingCalculations.retro_fit_changes(self.building_bad, self.settings_bad, 2030)
        retro_fit_changes_bad_2035 = BuildingCalculations.retro_fit_changes(self.building_bad, self.settings_bad, 2035)
        self.assertEqual(round(retro_fit_changes_good_2034, 3), 2.437)
        self.assertEqual(round(retro_fit_changes_good_2035, 0), 0)
        self.assertEqual(round(retro_fit_changes_bad_2029, 3), 43.748)
        self.assertEqual(round(retro_fit_changes_bad_2030, 3), 12.316)
        self.assertEqual(round(retro_fit_changes_bad_2035, 3), 9.038)
        
if __name__ == "__main__":
    unittest.main(verbosity=2)
    
