from .__all_models import Period, Material, Region
from .db_session import create_session


PERIODS = ('STAL', 'HRUSCH', 'BRZH', 'GORB', 'ELTS', 'PTN')
MATS = ('Panel', 'Brick', 'Block', 'Monolith')
REGIONS = ('I (North)', 'II (Moderate)', 'III (Warm)', 'IV (South)')


def validate_periods():
    db_sess = create_session()
    for i, _ in enumerate(PERIODS):
        if not db_sess.query(Period).filter(Period.name == _).first():
            db_sess.add(Period(id=i + 1, name=_))
    db_sess.commit()


def validate_materials():
    db_sess = create_session()
    for i, _ in enumerate(MATS):
        if not db_sess.query(Material).filter(Material.name == _).first():
            db_sess.add(Material(id=i + 1, name=_))
    db_sess.commit()


def validate_regions():
    db_sess = create_session()
    for i, _ in enumerate(REGIONS):
        if not db_sess.query(Region).filter(Region.name == _).first():
            db_sess.add(Region(id=i + 1, name=_))
    db_sess.commit()
