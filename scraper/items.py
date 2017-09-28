# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field
from scrapy.loader.processors import Compose, MapCompose
from scraper.utils import filter_empty, only_elem, only_elem_or_default


class MWJob(Item):
    timestamp = Field()
    url = Field()
    id = Field(input_processor=Compose(only_elem, unicode.strip))
    name = Field(input_processor=Compose(only_elem, unicode.strip))
    payment = Field(input_processor=Compose(float))
    success_pct = Field(input_processor=Compose(lambda v: v if v.lower() != 'n/a' else None, float))
    work_done = Field(input_processor=Compose(int))
    work_total = Field(input_processor=Compose(int))
    employer = Field()
    duration = Field(input_processor=Compose(int))
    countries = Field(input_processor=MapCompose(unicode.strip))
    category = Field(input_processor=Compose(only_elem_or_default))
    # sub_cat = Field(input_processor=Compose(only_elem_or_default))
    app_platform = Field()
    app_id = Field()
    expected = Field(input_processor=Compose(MapCompose(unicode.strip), filter_empty))
    proof = Field(input_processor=Compose(MapCompose(unicode.strip), filter_empty))

    @property
    def key(self):
        return self._values['id']

    @property
    def export_filename(self):
        return 'job'


class MWUser(Item):
    timestamp = Field()
    url = Field()
    id = Field(input_processor=Compose(only_elem, unicode.strip))
    name = Field(input_processor=Compose(only_elem, unicode.strip))
    member_since = Field(input_processor=Compose(only_elem, unicode.strip))
    country = Field(input_processor=Compose(only_elem_or_default))
    city = Field(input_processor=Compose(only_elem_or_default))
    total_earned = Field(input_processor=Compose(only_elem, float))
    tasks_done = Field(input_processor=Compose(only_elem, int))
    basic_tasks = Field(input_processor=Compose(only_elem, int))
    basic_satisfied = Field(input_processor=Compose(only_elem, int))
    basic_not_satisfied = Field(input_processor=Compose(only_elem, int))
    basic_avg_per_task = Field(input_processor=Compose(only_elem, float))
    hg_tasks = Field(input_processor=Compose(only_elem, int))
    hg_satisfied = Field(input_processor=Compose(only_elem, int))
    hg_not_satisfied = Field(input_processor=Compose(only_elem, int))
    hg_avg_per_task = Field(input_processor=Compose(only_elem, float))
    basic_campaigns = Field(input_processor=Compose(only_elem, int))
    basic_tasks_paid = Field(input_processor=Compose(only_elem, int))
    basic_total_paid = Field(input_processor=Compose(only_elem, unicode.strip, lambda v: v if v.lower() != 'n/a' else None, float))
    hg_campaigns = Field(input_processor=Compose(only_elem, int))
    hg_tasks_paid = Field(input_processor=Compose(only_elem, int))
    hg_total_paid = Field(input_processor=Compose(only_elem, unicode.strip, lambda v: v if v.lower() != 'n/a' else None, float))
    employer_type = Field(input_processor=Compose(only_elem))

    @property
    def key(self):
        return self._values['id']

    @property
    def export_filename(self):
        return 'user'


class RWJob(Item):
    timestamp = Field()
    url = Field()
    id = Field(input_processor=Compose(only_elem))
    name = Field(input_processor=Compose(only_elem, unicode.strip))
    payment = Field(input_processor=Compose(float))
    work_done = Field(input_processor=Compose(int))
    work_total = Field(input_processor=Compose(int))
    duration = Field(input_processor=Compose(int))
    countries = Field()
    # amazonUrls = Field(input_processor=Compose(MapCompose(unicode.strip), filter_empty))
    # proof = Field(input_processor=Compose(MapCompose(unicode.strip), filter_empty))
    # productId = Field()
    jobType = Field()
    amazonId = Field()
    

    @property
    def key(self):
        return self._values['amazonId']

    @property
    def export_filename(self):
        return 'seed'


class JBJob(Item):
    timestamp = Field()
    url = Field()
    id = Field(input_processor=Compose(only_elem))
    name = Field(input_processor=Compose(only_elem))
    payment = Field(input_processor=Compose(float))
    success_pct = Field(input_processor=Compose(float))
    work_done = Field(input_processor=Compose(int))
    work_total = Field(input_processor=Compose(int))
    duration = Field(input_processor=Compose(int))
    countries = Field()
    cat = Field(input_processor=Compose(only_elem))
    sub_cat = Field(input_processor=Compose(only_elem_or_default))
    expected = Field(input_processor=Compose(MapCompose(unicode.strip), filter_empty))
    proof = Field(input_processor=Compose(MapCompose(unicode.strip), filter_empty))

    @property
    def key(self):
        return self._values['id']

    @property
    def export_filename(self):
        return 'job'


class MFJob(Item):
    timestamp = Field()
    url = Field()
    id = Field(input_processor=Compose(only_elem))
    name = Field(input_processor=Compose(only_elem))
    payment = Field(input_processor=Compose(float))
    success_pct = Field(input_processor=Compose(float))
    work_done = Field(input_processor=Compose(int))
    work_total = Field(input_processor=Compose(int))
    duration = Field(input_processor=Compose(int))
    countries = Field()
    expected = Field(input_processor=Compose(MapCompose(unicode.strip), filter_empty))
    proof = Field(input_processor=Compose(MapCompose(unicode.strip), filter_empty))

    @property
    def key(self):
        return self._values['id']

    @property
    def export_filename(self):
        return 'job'


class CCJob(Item):
    timestamp = Field()
    url = Field()
    id = Field(input_processor=Compose(only_elem))
    name = Field(input_processor=Compose(only_elem, unicode.strip))
    payment = Field(input_processor=Compose(float))
    success_pct = Field(input_processor=Compose(only_elem_or_default, float))
    work_done = Field(input_processor=Compose(int))
    work_total = Field(input_processor=Compose(int))
    employer = Field()
    duration = Field(input_processor=Compose(only_elem, int))
    cat = Field(input_processor=Compose(only_elem, unicode.strip))
    featured = Field(input_processor=Compose(bool))
    expected = Field(input_processor=Compose(MapCompose(unicode.strip), filter_empty))
    proof = Field(input_processor=Compose(MapCompose(unicode.strip), filter_empty))
    countries = Field(input_processor=MapCompose(unicode.strip))

    @property
    def key(self):
        return self._values['id']

    @property
    def export_filename(self):
        return 'job'


class CCUser(Item):
    timestamp = Field()
    url = Field()
    id = Field(input_processor=Compose(only_elem))
    name = Field(input_processor=Compose(only_elem, unicode.strip))
    member_since = Field(input_processor=Compose(only_elem, unicode.strip))
    country = Field(input_processor=Compose(only_elem_or_default))
    tasks_done = Field(input_processor=Compose(only_elem, int))
    tasks_satisfied = Field(input_processor=Compose(only_elem, int))
    tasks_not_satisfied = Field(input_processor=Compose(only_elem, int))
    avg_per_task_earned = Field(input_processor=Compose(only_elem, float))
    total_earned = Field(input_processor=Compose(only_elem, float))
    tasks_paid = Field(input_processor=Compose(only_elem, int))
    avg_per_task_paid = Field(input_processor=Compose(only_elem, float))
    total_paid = Field(input_processor=Compose(only_elem, float))

    @property
    def key(self):
        return self._values['id']

    @property
    def export_filename(self):
        return 'user'


class STJob(Item):
    timestamp = Field()
    url = Field()
    id = Field()
    expire = Field()
    name = Field(input_processor=Compose(only_elem_or_default, unicode.strip))
    employer = Field(input_processor=Compose(only_elem, unicode.strip))
    payment = Field(input_processor=Compose(only_elem, float))
    work_remain = Field(input_processor=Compose(only_elem, int))
    duration = Field(input_processor=Compose(only_elem_or_default, int))
    expected = Field(input_processor=Compose(MapCompose(unicode.strip), filter_empty))

    @property
    def key(self):
        return self._values['id']

    @property
    def export_filename(self):
        return 'job'