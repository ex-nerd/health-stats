# -*- coding: utf-8 -*-

# python 2-3 compatibility
from builtins import super, int, object

from datetime import datetime

import re
import hashlib
# from pretty import pprint

from . import Base
from sqlalchemy import Column, String, DateTime, event
from sqlalchemy.orm import validates

# Some constants to keep track of the types of events
TYPE_NONE = ''
TYPE_INSULIN = 'insulin'
TYPE_GLUCOSE = 'glucose'
TYPE_CARBS = 'carbs'
TYPE_WEIGHT = 'weight'
TYPE_BLOOD_PRESSURE = 'bp'
TYPE_STEPS = 'steps'

# And for sources
SOURCE_ONETOUCH = 'ot'
SOURCE_MYSUGR = 'ms'
SOURCE_APPLE_HEALTH = 'ah'
SOURCE_DEXCOM_CLARITY = 'dc'

# Now map back to human names
SOURCE_NAME = {
    SOURCE_ONETOUCH: 'OneTouch',
    SOURCE_MYSUGR: 'MySugr',
    SOURCE_APPLE_HEALTH: 'Apple Health',
    SOURCE_DEXCOM_CLARITY: 'Dexcom Clarity',
}

class Event(Base):
    """ Abstract parent class representing a single log entry """

    __tablename__ = 'events'

    # @todo a primary key field (hash?) that's specific to each event type...

    id = Column(String, primary_key=True, nullable=False)
    time = Column(DateTime, nullable=False)
    type = Column(String, nullable=False)
    subtype = Column(String, nullable=True)
    source = Column(String, nullable=False)
    value = Column(String, nullable=False)
    unit = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    tags = Column(String, nullable=True)

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': TYPE_NONE,
    }

    def __init__(self, skip_id=False, **kwargs):
        super(Event, self).__init__(**kwargs)
        if not skip_id:
            self.id = self.generate_id()

    def generate_id(self):
        if None in (self.time, self.type, self.source, self.value, self.unit, ):
            # Not enough data to calculate
            return None
        else:
            # Turn the data we care about into a sha1 that should be unique enough for our purposes.
            data = (
                self.time,
                self.type,
                self.subtype,
                self.source,
                self.value,
                self.unit,
                self.notes,
                self.tags,
            )
            m = hashlib.sha1()
            m.update(repr(data))
            return m.hexdigest()

    @validates('time')
    def validate_time(self, key, time):
        # For better duplicate detection, remove any precision below one minute
        # (e.g. OneTouch only gives one-minute resolution)
        return datetime(
            year=time.year,
            month=time.month,
            day=time.day,
            hour=time.hour,
            minute=time.minute,
        )

    @validates('source')
    def validate_source(self, key, source):
        if source not in SOURCE_NAME.keys():
            raise ValueError('Unrecognized source type at {}: {}'.format(self.time, source))
        return source

    def __cmp__(self, other):
        if isinstance(other, Event):
            if self.time == other.time:
                if self.type == other.type:
                    if self.subtype == other.subtype:
                        if self.source == other.source:
                            if self.unit == other.unit:
                                return cmp(self.value, other.value)
                            return cmp(self.unit, other.unit)
                        return cmp(self.source, other.source)
                    return cmp(self.subtype, other.subtype)
                return cmp(self.type, other.type)
            return cmp(self.time, other.time)
        try:
            return cmp(self.time, other)
        except TypeError as e:
            # print("Can't compare {} to {}".format(self, other))
            raise e

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __le__(self, other):
        return self.__cmp__(other) <= 0

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __ge__(self, other):
        return self.__cmp__(other) >= 0

    def __hash__(self):
        # No need to include notes/tags in the hash -- in fact, it's better to
        # exclude them e.g. so that two "equal" instances could later have
        # their notes/tags merged together.
        return hash((self.time, self.type, self.subtype, self.unit, self.value, ))

    def __repr__(self):
        return "<{}(source='{}', time='{}', type='{}', subtype='{}', value='{}', unit='{}', ...)>".format(
            self.__class__.__name__, self.source, self.time, self.type, self.subtype, self.value, self.unit
        )

    def __pretty__(self, p, cycle):
        p.text('<{0}: '.format(type(self).__name__))
        if cycle:
            p.text(str(self.time))
        else:
            p.text(', '.join([str(self.source), str(self.time), str(self.type), str(self.subtype), str(self.value), str(self.unit)]))
        p.text('>')


class InsulinEvent(Event):
    """ Event type representing a dose of insulin """

    __mapper_args__ = {
        'polymorphic_identity': TYPE_INSULIN,
    }

    UNIT_U = 'u'

    TYPE_RAPID = 'rapid'
    TYPE_LONG = 'long'
    TYPE_OTHER = 'other'

    def __init__(self, **kwargs):
        super(InsulinEvent, self).__init__(skip_id=True, **kwargs)
        if self.unit is None:
            self.unit = self.UNIT_U
        # Now that we have a unit, (re)generate the id
        self.id = self.generate_id()

    @validates('subtype')
    def validate_subtype(self, key, subtype):
        if subtype not in (self.TYPE_RAPID, self.TYPE_LONG, ):
            raise ValueError('Unrecognized insulin type at {}: {}'.format(self.time, subtype))
        return subtype

    @validates('value')
    def validate_value(self, key, value):
        if int(value) != value:
            raise ValueError('Invalid non-integer insulin value at {}: {}'.format(self.time, value))
        if value < 1:
            raise ValueError('Invalid insulin value at {}: {} < 1'.format(self.time, value))
        return value


class GlucoseEvent(Event):
    """ Event type representing a blood-glucose reading """

    __mapper_args__ = {
        'polymorphic_identity': TYPE_GLUCOSE
    }

    UNIT_MGDL = 'mg/dL'

    TYPE_METER = 'm'
    TYPE_CGM = 'cgm'

    def __init__(self, **kwargs):
        super(GlucoseEvent, self).__init__(skip_id=True, **kwargs)
        if self.unit is None:
            self.unit = self.UNIT_MGDL
        # Now that we have a unit, (re)generate the id
        self.id = self.generate_id()

    @validates('value')
    def validate_value(self, key, value):
        # Yeah, I know you'd be dead at 1, but let's not make any judgments
        if value < 1:
            raise ValueError('Invalid glucose value at {}: {} < 1'.format(self.time, value))
        return value


class CarbsEvent(Event):
    """ Event type representing a blood-glucose reading """

    __mapper_args__ = {
        'polymorphic_identity': TYPE_CARBS,
    }

    @validates('value')
    def validate_value(self, key, value):
        # Zero carbs is ok (alcohol) but don't allow negative
        if value < 0:
            raise ValueError('Invalid negative carbs value at {}: {}'.format(self.time, value))
        return value


class WeightEvent(Event):
    """ Event type representing a blood-glucose reading """

    __mapper_args__ = {
        'polymorphic_identity': TYPE_WEIGHT,
    }

    UNIT_KG = 'kg'
    UNIT_LB = 'lb'

    @validates('value')
    def validate_value(self, key, value):
        if value < 1:
            raise ValueError('Invalid weight value at {}: {} < 1'.format(self.time, value))
        return value

    @validates('unit')
    def validate_unit(self, key, unit):
        if unit not in (self.UNIT_KG, self.UNIT_LB, ):
            raise ValueError('Unrecognized weight unit at {}: {}'.format(self.time, unit))
        return unit


class BloodPressureEvent(Event):
    """ Event type representing a blood-glucose reading """

    __mapper_args__ = {
        'polymorphic_identity': TYPE_BLOOD_PRESSURE,
    }

    @validates('value')
    def validate_value(self, key, value):
        if re.match(r'^\d{2,3}/\d{2,3}$', value) is None:
            raise ValueError('Unrecognized blood pressure value at {}: {}'.format(self.time, value))
        return value


class StepsEvent(Event):
    """ Event type representing a count of steps """

    __mapper_args__ = {
        'polymorphic_identity': TYPE_STEPS,
    }

    @validates('value')
    def validate_value(self, key, value):
        if value < 1:
            raise ValueError('Unrecognized steps value at {}: {}'.format(self.time, value))
        return value
