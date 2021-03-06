from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from annoying.decorators import render_to
from blockexplorer.decorators import assert_valid_coin_symbol

from blockexplorer.settings import BLOCKCYPHER_API_KEY

from blockcypher.api import get_block_details, get_block_overview_url, get_latest_block_height

from utils import get_max_pages


@assert_valid_coin_symbol
@render_to('block_overview.html')
def block_overview(request, coin_symbol, block_representation):

    TXNS_PER_PAGE = 20

    # 1 indexed page
    current_page = request.GET.get('page')
    if current_page:
        current_page = int(current_page)
    else:
        current_page = 1

    # TODO: fail gracefully if the user picks a number of pages that is too large
    # Waiting on @matthieu's change to API first (currently throws 502)

    try:
        block_details = get_block_details(
                block_representation=block_representation,
                coin_symbol=coin_symbol,
                txn_limit=TXNS_PER_PAGE,
                txn_offset=(current_page-1)*TXNS_PER_PAGE,
                api_key=BLOCKCYPHER_API_KEY,
                )
    except AssertionError:
        msg = _('Invalid Block Representation')
        messages.warning(request, msg)
        redir_url = reverse('coin_overview', kwargs={'coin_symbol': coin_symbol})
        return HttpResponseRedirect(redir_url)

    # import pprint; pprint.pprint(block_details, width=1)

    if 'error' in block_details:
        msg = _('Sorry, that block was not found')
        messages.warning(request, msg)
        return HttpResponseRedirect(reverse('home'))

    # Technically this is not the only API call used on this page
    api_url = get_block_overview_url(block_representation=block_representation, coin_symbol=coin_symbol)

    return {
            'coin_symbol': coin_symbol,
            'api_url': api_url,
            'block_details': block_details,
            'current_page': current_page,
            'max_pages': get_max_pages(num_items=block_details['n_tx'], items_per_page=TXNS_PER_PAGE),
            }


@assert_valid_coin_symbol
def latest_block(request, coin_symbol):
    latest_block_height = get_latest_block_height(coin_symbol=coin_symbol,
            api_key=BLOCKCYPHER_API_KEY)
    kwargs = {
            'coin_symbol': coin_symbol,
            'block_representation': latest_block_height,
            }
    return HttpResponseRedirect(reverse('block_overview', kwargs=kwargs))
