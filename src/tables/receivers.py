
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db.models import loading
from tables.models import Table, Field
from tables import table_build

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Table)
def update_flight_modified_date(instance, **kwargs):
    print('sig')
    table_build.remove_table(table_build.get_model(instance))


# django.db.models.loading.  It took me a good couple of hours walking back
# through the entire process a new Model goes through (after my newly created
# ones weren’t showing up properly) before I found this little tidbit.
#  The fix was simple enough, since the cache is keyed off the app and model name,
# I just had to delete my model’s entry every time it’s DynamicModel record was saved.
