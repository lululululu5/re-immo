from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional
import enum

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


class UserTypes(enum.Enum):
    general = "general"
    partner = "partner"
    admin = "admin"
    
class PropertyTypes(enum.Enum):
    residential_single_family = "RSF"
    residential_multi_family = "RMF"
    
class EnergyTypes(enum.Enum):
    biogas = "Biogas"
    wood_chips = "Wood chips"
    wood_pellets = "Wood pellets"
    coal = "Coal"
    landfill_gas = "Landfill gas"
    lpgs = "LPGs"

class FGasTypes(enum.Enum):
    CARBON_DIOXIDE_CO2 = "Carbon dioxide (CO2)"
    METHANE_CH4 = "Methane (CH4)"
    NITROUS_OXIDE_N2O = "Nitrous oxide (N2O)"
    R_11 = "R-11"
    CFC_11 = "CFC-11"
    TRICHLOROFLUOROMETHANE_CCI3F = "Trichlorofluoromethane (CCI3F)"
    R_12 = "R-12"
    CFC_12 = "CFC-12"
    DICHLOROFLUOROMETHANE_CCI2F2 = "Dichlorofluoromethane (CCI2F2)"
    R_13 = "R-13"
    CFC_13 = "CFC-13"
    CHLORODIFLUOROMETHANE_CCIF3 = "Chlorodifluoromethane (CCIF3)"
    R_113 = "R-113"
    CFC_113 = "CFC-113"
    TRICHLOROTRIFLUOROETHANE_C2CI3F3 = "1,1,2-Trichloro-1,2,2-trifluoroethane (C2CI3F3)"
    R_114 = "R-114"
    CFC_114 = "CFC-114"
    HALON_242 = "Halon-242"
    DICHLOROTETRAFLUOROETHANE_C2Cl2F4 = "1,2-Dichlorotetrafluoroethane (C2Cl2F4)"
    R_115 = "R-115"
    CFC_115 = "CFC-115"
    CHLOROPENTAFLUOROETHANE_C2ClF5 = "Chloropentafluoroethane (C2ClF5)"
    R13_B1 = "R13 B1"
    HALON_1301 = "Halon-1301"
    BROMOTRIFLUOROMETHANE_CBrF3 = "Bromotrifluoromethane (CBrF3)"
    R_12B1 = "R-12B1"
    HALON_1211 = "Halon-1211"
    BROMOCHLORODIFLUOROMETHANE_CBrCIF2 = "Bromochlorodifluoromethane (CBrCIF2)"
    R_114B2 = "R 114B2"
    HALON_2402 = "Halon-2402"
    DIBROMOTETRAFLUOROETHANE_C2Br2F4 = "1,2-Dibromotetrafluoroethane (C2Br2F4)"
    R_10 = "R-10"
    CARBON_TETRACHLORIDE_CCl4 = "Carbon tetrachloride (CCl4)"
    BROMOMETHANE = "Bromomethane"
    METHYL_BROMIDE_CH3Br = "Methyl bromide (CH3Br)"
    R_140a = "R-140a"
    TRICHLOROETHANE = "1,1,1- Trichloroethane"
    METHYL_CHLOROFORM_C2H3Cl3 = "Methyl chloroform (C2H3Cl3)"
    R_21 = "R-21"
    HCFC_21 = "HCFC-21"
    DICHLOROFLUOROMETHANE_CHCl2F = "Dichlorofluoromethane (CHCl2F)"
    R_22 = "R-22"
    HCFC_22 = "HCFC-22"
    CHLORODIFLUOROMETHANE_CHClF2 = "Chlorodifluoromethane (CHClF2)"
    R_123 = "R-123"
    HCFC_123 = "HCFC-123"
    DICHLOROTRIFLUOROETHANE_C2Cl2F3 = "2,2-Dichloro-1,1,1-trifluoroethane (C2Cl2F3)"
    R_124 = "R-124"
    HCFC_124 = "HCFC-124"
    TETRAFLUOROETHANE_C2ClF4 = "1-Chloro-1,2,2,2-tetrafluoroethane (C2ClF4)"
    R_141b = "R-141b"
    HCFC_141b = "HCFC-141b"
    DICHLOROFLUOROETHANE_C2H3Cl2F = "1,1,-Dichloro-1-1-fluoroethane (C2H3Cl2F)"
    R_142b = "R-142b"
    HCFC_142b = "HCFC-142b"
    DICHLORODIFLUOROETHANE_C2ClF2 = "1-Chloro-1,1,-difluoroethane (C2ClF2)"
    R_225ca = "R-225ca"
    HCFC_225ca = "HCFC-225ca"
    DICHLOROPENTAFLUOROPROPANE_C3HCl2F5 = "3.3-dichloro-1,1,1,2,2-pentafluoropropane (C3HCl2F5)"
    R_225cb = "R-225cb"
    HCFC_225cb = "HCFC-225cb"
    PENTAFLUOROPROPANE_C3HCl2F5 = "1,3-Dichloro-1,1,2,2,3-pentafluoropropane (C3HCl2F5)"
    R_23 = "R-23"
    HFC_23 = "HFC-23"
    R_32 = "R-32"
    HFC_32 = "HFC-32"
    R_41 = "R-41"
    HFC_41 = "HFC-41"
    R_125 = "R-125"
    HFC_125 = "HFC-125"
    R_134 = "R-134"
    HFC_134 = "HFC-134"
    R_134a = "R-134a"
    HFC_134a = "HFC-134a"
    R_143 = "R-143"
    HFC_143 = "HFC-143"
    R_143a = "R-143a"
    HFC_143a = "HFC-143a"
    R_152 = "R-152"
    HFC_152 = "HFC-152"
    R_152a = "R-152a"
    HFC_152a = "HFC-152a"
    R_161 = "R-161"
    HFC_161 = "HFC-161"
    R_227ea = "R-227ea"
    HFC_227ea = "HFC-227ea"
    R_236cb = "R-236cb"
    HFC_236cb = "HFC-236cb"
    R_404A = "R-404A"
    R_407C = "R-407C"
    R_410A = "R-410A"
    R_422D = "R-422D"
    R_448A = "R-448A"
    R_449A = "R-449A"
    SULFUR_HEXAFLUORIDE_SF6 = "Sulfur hexafluoride (SF6)"
    NITROGEN_TRIFLUORIDE_NF3 = "Nitrogen trifluoride (NF3)"



class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id: so.Mapped[str] = so.mapped_column(sa.String(64), primary_key=True, index=True, default=lambda:str(uuid4()))
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    user_type: so.Mapped[UserTypes] = so.mapped_column(sa.Enum(UserTypes, validate_strings=True), default=UserTypes.general)
    
    #relationship
    building: so.Mapped["Building"] = so.relationship(back_populates="owner")
    
    def set_password(self, password):
        # Add additional criteria for stable password
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
    
    def __repr__(self) -> str:
        return f"<User: {self.name} Email: {self.email} >"
    
@login.user_loader
def load_user(id):
    return db.session.get(User, id)


class Building(db.Model):
    __tablename__ = "buildings"
    
    id: so.Mapped[str] = so.mapped_column(sa.String(64), primary_key=True, default=lambda:str(uuid4()))
    address: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, nullable=False)
    reporting_year: so.Mapped[int] = so.mapped_column(nullable=False, default=lambda:datetime.date.today().year)
    country: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=False)
    zip: so.Mapped[str] = so.mapped_column(sa.String(16), nullable=False)
    property_type: so.Mapped[PropertyTypes] = so.mapped_column(sa.Enum(PropertyTypes, validate_strings=True), default=PropertyTypes.residential_single_family)
    size: so.Mapped[float] = so.mapped_column(nullable=False)
    
    #Energy Procurement
    grid_elec: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)
    natural_gas: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)
    fuel_oil: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)
    dist_heating: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)
    dist_cooling: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)
    o1_energy_type: so.Mapped[Optional[EnergyTypes]] = so.mapped_column(sa.Enum(EnergyTypes, validate_strings=True), nullable=True)
    o1_consumption: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)
    #these two cannot be the same energy_type. Create validation. 
    o2_energy_type: so.Mapped[Optional[EnergyTypes]] = so.mapped_column(sa.Enum(EnergyTypes, validate_strings=True), nullable=True)
    o2_consumption: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)
    
    #Fugitive Emissions
    f_gas_1_type: so.Mapped[Optional[FGasTypes]] = so.mapped_column(sa.Enum(FGasTypes, validate_strings=True), nullable=True)
    f_gas_1_amount: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)
    #these two cannot be the same f_gas_type. Create validation.
    f_gas_2_type: so.Mapped[Optional[FGasTypes]] = so.mapped_column(sa.Enum(FGasTypes, validate_strings=True), nullable=True)
    f_gas_2_amount: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)
    
     # Renewable energy
    pv_wind_consumed: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)
    pv_wind_exported: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)
    hp_solar_consumed: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)
    hp_solar_exported: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)
    off_site_renewables: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)

    # Retrofit
    retrofit_year: so.Mapped[Optional[int]] = so.mapped_column(nullable=True)
    retrofit_investment: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)
    
    __table_args__ = (
        sa.CheckConstraint("size >= 0", name="check_size_non_negative"),
        sa.CheckConstraint("grid_elec >= 0", name="check_grid_elec_non_negative"),
        sa.CheckConstraint("natural_gas >= 0", name="check_natural_gas_non_negative"),
        sa.CheckConstraint("fuel_oil >= 0", name="check_fuel_oil_non_negative"),
        sa.CheckConstraint("dist_heating >= 0", name="check_dist_heating_non_negative"),
        sa.CheckConstraint("dist_cooling >= 0", name="check_dist_cooling_non_negative"),
        sa.CheckConstraint("o1_consumption >= 0", name="check_o1_consumption_non_negative"),
        sa.CheckConstraint("o2_consumption >= 0", name="check_o2_consumption_non_negative"),
        sa.CheckConstraint("f_gas_1_amount >= 0", name="check_f_gas_1_amount_non_negative"),
        sa.CheckConstraint("f_gas_2_amount >= 0", name="check_f_gas_2_amount_non_negative"),
        sa.CheckConstraint("pv_wind_consumed >= 0", name="check_pv_wind_consumed_non_negative"),
        sa.CheckConstraint("pv_wind_exported >= 0", name="check_pv_wind_exported_non_negative"),
        sa.CheckConstraint("hp_solar_consumed >= 0", name="check_hp_solar_consumed_non_negative"),
        sa.CheckConstraint("hp_solar_exported >= 0", name="check_hp_solar_exported_non_negative"),
        sa.CheckConstraint("off_site_renewables >= 0", name="check_off_site_renewables_non_negative"),
        sa.CheckConstraint("retrofit_investment >= 0", name="check_retrofit_investment_non_negative"),
    )
    
    user_id: so.Mapped[str] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    #relationship
    owner: so.Mapped[User] = so.relationship(back_populates="building")

    
    

# class Building(db.Model):
#     __tablename__ = "buildings"
    
#     id: so.Mapped[int] = so.mapped_column(primary_key=True)
#     user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
#     address: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    
    
    
    
    
#     def __repr__(self) -> str:
#         return f"Building {self.address}"
    

    
    