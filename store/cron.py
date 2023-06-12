import logging
import os
import calendar
import datetime
from store.models import *


# python manage.py crontab add
# python manage.py crontab show
# python manage.py crontab remove



logger = logging.getLogger(__name__)



def InactiveExpiredDeals():

    try:
        logger.info("--------------API Called-------------")

        deals = BusinessDeal.objects.filter(end_date__lte=datetime.datetime.now(), is_expired=False, deal_status='Active')
        if deals:
            for deal in deals:
                deal.is_expired = True
                deal.deal_status = 'Inactive'
                deal.save()
            logger.info("--------------Deasl Expired And Inactive Successfully-------------")
        else:
            logger.info("--------------Deasl Not Found-------------")
    except Exception as e:
        logger.info(e.args[0])

