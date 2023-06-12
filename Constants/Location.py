
from django.contrib.gis.geoip2 import GeoIP2

def get_user_current_location(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
       ip = x_forwarded_for.split(',')[0]
    else:
       ip = request.META.get('REMOTE_ADDR')
       
    g = GeoIP2()
    # ip = '2400:adc5:1e1:d400:7145:9821:b22f:7be9'

    # print(g.lat_lon(ip))
    # print(g.country_name(ip))
    # print(g.country_code(ip))
    # print(g.lon_lat(ip))
    # print(g.city(ip))
    # print(g.city(ip)['city'])
    data = {
        'ip' : ip
    }
    try:
        location = g.city(ip)
    except:
        ip = '2400:adc5:1e1:d400:7145:9821:b22f:7be9'
        location = g.city(ip)
        
    try:
        data['country'] = location['country_name']
        data.update(location)
    except Exception as err:
        print(err)
        data['country'] = None

    return data