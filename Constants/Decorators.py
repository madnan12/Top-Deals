

from django.shortcuts import redirect
from .Location import get_user_current_location



def LocationRedirection(func):
    def SubDecotrator(*args, country_code=None,  **kwargs):
        request= args[0]
        if request.method == 'GET':
            if country_code is None:
                location_data = get_user_current_location(request)
                user_loc_country_code = location_data.get('country_code', None)
                if user_loc_country_code is not None:
                    queries = ''
                    for index, query in enumerate(request.GET.items()):
                        ky, val = query
                        if index > 0:
                            queries += '&'
                        else:
                            queries += '?'
                        queries += f'{ky}={val}'
                    return redirect(f'/{user_loc_country_code.lower()}{request.META["PATH_INFO"]}{queries}')
        
        try:
            request.META._mutable = True
        except:
            pass
        request.META['country_code']= country_code

    
        return func(*args, country_code=country_code, **kwargs)
    return SubDecotrator
    
