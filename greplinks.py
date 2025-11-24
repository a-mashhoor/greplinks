#!/usr/bin/env python3

import argparse
import re
import sys
import ipaddress
import textwrap
import os
import socket
import urllib.request
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

TLD_CACHE_PATH = os.path.expanduser("~/.tld_cache.txt")


FALLBACK_TLDS = {'aaa', 'aarp', 'abb', 'abbott', 'abbvie', 'abc', 'able', 'abogado',
     'abudhabi', 'ac', 'academy', 'accenture', 'accountant', 'accountants', 'aco',
     'actor', 'ad', 'ads', 'adult', 'ae', 'aeg', 'aero', 'aetna', 'af', 'afl',
     'africa', 'ag', 'agakhan', 'agency', 'ai', 'aig', 'airbus', 'airforce',
     'airtel', 'akdn', 'al', 'alibaba', 'alipay', 'allfinanz', 'allstate', 'ally',
     'alsace', 'alstom', 'am', 'amazon', 'americanexpress', 'americanfamily',
     'amex', 'amfam', 'amica', 'amsterdam', 'analytics', 'android', 'anquan',
     'anz', 'ao', 'aol', 'apartments', 'app', 'apple', 'aq', 'aquarelle', 'ar',
     'arab', 'aramco', 'archi', 'army', 'arpa', 'art', 'arte', 'as', 'asda',
     'asia', 'associates', 'at', 'athleta', 'attorney', 'au', 'auction', 'audi',
     'audible', 'audio', 'auspost', 'author', 'auto', 'autos', 'aw', 'aws', 'ax',
     'axa', 'az', 'azure', 'ba', 'baby', 'baidu', 'banamex', 'band', 'bank', 'bar',
     'barcelona', 'barclaycard', 'barclays', 'barefoot', 'bargains', 'baseball',
     'basketball', 'bauhaus', 'bayern', 'bb', 'bbc', 'bbt', 'bbva', 'bcg', 'bcn',
     'bd', 'be', 'beats', 'beauty', 'beer', 'berlin', 'best', 'bestbuy', 'bet',
     'bf', 'bg', 'bh', 'bharti', 'bi', 'bible', 'bid', 'bike', 'bing', 'bingo',
     'bio', 'biz', 'bj', 'black', 'blackfriday', 'blockbuster', 'blog',
     'bloomberg', 'blue', 'bm', 'bms', 'bmw', 'bn', 'bnpparibas', 'bo', 'boats',
     'boehringer', 'bofa', 'bom', 'bond', 'boo', 'book', 'booking', 'bosch',
     'bostik', 'boston', 'bot', 'boutique', 'box', 'br', 'bradesco', 'bridgestone',
     'broadway', 'broker', 'brother', 'brussels', 'bs', 'bt', 'build', 'builders',
     'business', 'buy', 'buzz', 'bv', 'bw', 'by', 'bz', 'bzh', 'ca', 'cab', 'cafe',
     'cal', 'call', 'calvinklein', 'cam', 'camera', 'camp', 'canon', 'capetown',
     'capital', 'capitalone', 'car', 'caravan', 'cards', 'care', 'career',
     'careers', 'cars', 'casa', 'case', 'cash', 'casino', 'cat', 'catering',
     'catholic', 'cba', 'cbn', 'cbre', 'cc', 'cd', 'center', 'ceo', 'cern', 'cf',
     'cfa', 'cfd', 'cg', 'ch', 'chanel', 'channel', 'charity', 'chase', 'chat',
     'cheap', 'chintai', 'christmas', 'chrome', 'church', 'ci', 'cipriani',
     'circle', 'cisco', 'citadel', 'citi', 'citic', 'city', 'ck', 'cl', 'claims',
     'cleaning', 'click', 'clinic', 'clinique', 'clothing', 'cloud', 'club',
     'clubmed', 'cm', 'cn', 'co', 'coach', 'codes', 'coffee', 'college', 'cologne',
     'com', 'commbank', 'community', 'company', 'compare', 'computer', 'comsec',
     'condos', 'construction', 'consulting', 'contact', 'contractors', 'cooking',
     'cool', 'coop', 'corsica', 'country', 'coupon', 'coupons', 'courses', 'cpa',
     'cr', 'credit', 'creditcard', 'creditunion', 'cricket', 'crown', 'crs',
     'cruise', 'cruises', 'cu', 'cuisinella', 'cv', 'cw', 'cx', 'cy', 'cymru',
     'cyou', 'cz', 'dad', 'dance', 'data', 'date', 'dating', 'datsun', 'day',
     'dclk', 'dds', 'de', 'deal', 'dealer', 'deals', 'degree', 'delivery', 'dell',
     'deloitte', 'delta', 'democrat', 'dental', 'dentist', 'desi', 'design', 'dev',
     'dhl', 'diamonds', 'diet', 'digital', 'direct', 'directory', 'discount',
     'discover', 'dish', 'diy', 'dj', 'dk', 'dm', 'dnp', 'do', 'docs', 'doctor',
     'dog', 'domains', 'dot', 'download', 'drive', 'dtv', 'dubai', 'dupont',
     'durban', 'dvag', 'dvr', 'dz', 'earth', 'eat', 'ec', 'eco', 'edeka', 'edu',
     'education', 'ee', 'eg', 'email', 'emerck', 'energy', 'engineer',
     'engineering', 'enterprises', 'epson', 'equipment', 'er', 'ericsson', 'erni',
     'es', 'esq', 'estate', 'et', 'eu', 'eurovision', 'eus', 'events', 'exchange',
     'expert', 'exposed', 'express', 'extraspace', 'fage', 'fail', 'fairwinds',
     'faith', 'family', 'fan', 'fans', 'farm', 'farmers', 'fashion', 'fast',
     'fedex', 'feedback', 'ferrari', 'ferrero', 'fi', 'fidelity', 'fido', 'film',
     'final', 'finance', 'financial', 'fire', 'firestone', 'firmdale', 'fish',
     'fishing', 'fit', 'fitness', 'fj', 'fk', 'flickr', 'flights', 'flir',
    'florist', 'flowers', 'fly', 'fm', 'fo', 'foo', 'food', 'football', 'ford',
    'forex', 'forsale', 'forum', 'foundation', 'fox', 'fr', 'free', 'fresenius',
    'frl', 'frogans', 'frontier', 'ftr', 'fujitsu', 'fun', 'fund', 'furniture',
    'futbol', 'fyi', 'ga', 'gal', 'gallery', 'gallo', 'gallup', 'game', 'games',
    'gap', 'garden', 'gay', 'gb', 'gbiz', 'gd', 'gdn', 'ge', 'gea', 'gent',
    'genting', 'george', 'gf', 'gg', 'ggee', 'gh', 'gi', 'gift', 'gifts', 'gives',
    'giving', 'gl', 'glass', 'gle', 'global', 'globo', 'gm', 'gmail', 'gmbh',
    'gmo', 'gmx', 'gn', 'godaddy', 'gold', 'goldpoint', 'golf', 'goo', 'goodyear',
    'goog', 'google', 'gop', 'got', 'gov', 'gp', 'gq', 'gr', 'grainger',
    'graphics', 'gratis', 'green', 'gripe', 'grocery', 'group', 'gs', 'gt', 'gu',
    'gucci', 'guge', 'guide', 'guitars', 'guru', 'gw', 'gy', 'hair', 'hamburg',
    'hangout', 'haus', 'hbo', 'hdfc', 'hdfcbank', 'health', 'healthcare', 'help',
    'helsinki', 'here', 'hermes', 'hiphop', 'hisamitsu', 'hitachi', 'hiv', 'hk',
    'hkt', 'hm', 'hn', 'hockey', 'holdings', 'holiday', 'homedepot', 'homegoods',
    'homes', 'homesense', 'honda', 'horse', 'hospital', 'host', 'hosting', 'hot',
    'hotels', 'hotmail', 'house', 'how', 'hr', 'hsbc', 'ht', 'hu', 'hughes',
    'hyatt', 'hyundai', 'ibm', 'icbc', 'ice', 'icu', 'id', 'ie', 'ieee', 'ifm',
    'ikano', 'il', 'im', 'imamat', 'imdb', 'immo', 'immobilien', 'in', 'inc',
    'industries', 'infiniti', 'info', 'ing', 'ink', 'institute', 'insurance',
    'insure', 'int', 'international', 'intuit', 'investments', 'io', 'ipiranga',
    'iq', 'ir', 'irish', 'is', 'ismaili', 'ist', 'istanbul', 'it', 'itau', 'itv',
    'jaguar', 'java', 'jcb', 'je', 'jeep', 'jetzt', 'jewelry', 'jio', 'jll', 'jm',
    'jmp', 'jnj', 'jo', 'jobs', 'joburg', 'jot', 'joy', 'jp', 'jpmorgan', 'jprs',
    'juegos', 'juniper', 'kaufen', 'kddi', 'ke', 'kerryhotels', 'kerryproperties',
    'kfh', 'kg', 'kh', 'ki', 'kia', 'kids', 'kim', 'kindle', 'kitchen', 'kiwi',
    'km', 'kn', 'koeln', 'komatsu', 'kosher', 'kp', 'kpmg', 'kpn', 'kr', 'krd',
    'kred', 'kuokgroup', 'kw', 'ky', 'kyoto', 'kz', 'la', 'lacaixa', 'lamborghini',
    'lamer', 'land', 'landrover', 'lanxess', 'lasalle', 'lat', 'latino', 'latrobe',
    'law', 'lawyer', 'lb', 'lc', 'lds', 'lease', 'leclerc', 'lefrak', 'legal',
    'lego', 'lexus', 'lgbt', 'li', 'lidl', 'life', 'lifeinsurance', 'lifestyle',
    'lighting', 'like', 'lilly', 'limited', 'limo', 'lincoln', 'link', 'live',
    'living', 'lk', 'llc', 'llp', 'loan', 'loans', 'locker', 'locus', 'lol',
    'london', 'lotte', 'lotto', 'love', 'lpl', 'lplfinancial', 'lr', 'ls', 'lt',
    'ltd', 'ltda', 'lu', 'lundbeck', 'luxe', 'luxury', 'lv', 'ly', 'ma', 'madrid',
    'maif', 'maison', 'makeup', 'man', 'management', 'mango', 'map', 'market',
    'marketing', 'markets', 'marriott', 'marshalls', 'mattel', 'mba', 'mc',
    'mckinsey', 'md', 'me', 'med', 'media', 'meet', 'melbourne', 'meme',
    'memorial', 'men', 'menu', 'merckmsd', 'mg', 'mh', 'miami', 'microsoft', 'mil',
    'mini', 'mint', 'mit', 'mitsubishi', 'mk', 'ml', 'mlb', 'mls', 'mm', 'mma',
    'mn', 'mo', 'mobi', 'mobile', 'moda', 'moe', 'moi', 'mom', 'monash', 'money',
    'monster', 'mormon', 'mortgage', 'moscow', 'moto', 'motorcycles', 'mov',
    'movie', 'mp', 'mq', 'mr', 'ms', 'msd', 'mt', 'mtn', 'mtr', 'mu', 'museum',
    'music', 'mv', 'mw', 'mx', 'my', 'mz', 'na', 'nab', 'nagoya', 'name', 'navy',
    'nba', 'nc', 'ne', 'nec', 'net', 'netbank', 'netflix', 'network', 'neustar',
    'new', 'news', 'next', 'nextdirect', 'nexus', 'nf', 'nfl', 'ng', 'ngo', 'nhk',
    'ni', 'nico', 'nike', 'nikon', 'ninja', 'nissan', 'nissay', 'nl', 'no',
    'nokia', 'norton', 'now', 'nowruz', 'nowtv', 'np', 'nr', 'nra', 'nrw', 'ntt',
    'nu', 'nyc', 'nz', 'obi', 'observer', 'office', 'okinawa', 'olayan',
    'olayangroup', 'ollo', 'om', 'omega', 'one', 'ong', 'onl', 'online', 'ooo',
    'open', 'oracle', 'orange', 'org', 'organic', 'origins', 'osaka', 'otsuka',
    'ott', 'ovh', 'pa', 'page', 'panasonic', 'paris', 'pars', 'partners', 'parts',
    'party', 'pay', 'pccw', 'pe', 'pet', 'pf', 'pfizer', 'pg', 'ph', 'pharmacy',
    'phd', 'philips', 'phone', 'photo', 'photography', 'photos', 'physio', 'pics',
    'pictet', 'pictures', 'pid', 'pin', 'ping', 'pink', 'pioneer', 'pizza', 'pk',
    'pl', 'place', 'play', 'playstation', 'plumbing', 'plus', 'pm', 'pn', 'pnc',
    'pohl', 'poker', 'politie', 'porn', 'post', 'pr', 'praxi', 'press', 'prime',
    'pro', 'prod', 'productions', 'prof', 'progressive', 'promo', 'properties',
    'property', 'protection', 'pru', 'prudential', 'ps', 'pt', 'pub', 'pw', 'pwc',
    'py', 'qa', 'qpon', 'quebec', 'quest', 'racing', 'radio', 're', 'read',
    'realestate', 'realtor', 'realty', 'recipes', 'red', 'redumbrella', 'rehab',
    'reise', 'reisen', 'reit', 'reliance', 'ren', 'rent', 'rentals', 'repair',
    'report', 'republican', 'rest', 'restaurant', 'review', 'reviews', 'rexroth',
    'rich', 'richardli', 'ricoh', 'ril', 'rio', 'rip', 'ro', 'rocks', 'rodeo',
    'rogers', 'room', 'rs', 'rsvp', 'ru', 'rugby', 'ruhr', 'run', 'rw', 'rwe',
    'ryukyu', 'sa', 'saarland', 'safe', 'safety', 'sakura', 'sale', 'salon',
    'samsclub', 'samsung', 'sandvik', 'sandvikcoromant', 'sanofi', 'sap', 'sarl',
    'sas', 'save', 'saxo', 'sb', 'sbi', 'sbs', 'sc', 'scb', 'schaeffler',
    'schmidt', 'scholarships', 'school', 'schule', 'schwarz', 'science', 'scot',
    'sd', 'se', 'search', 'seat', 'secure', 'security', 'seek', 'select', 'sener',
    'services', 'seven', 'sew', 'sex', 'sexy', 'sfr', 'sg', 'sh', 'shangrila',
    'sharp', 'shell', 'shia', 'shiksha', 'shoes', 'shop', 'shopping', 'shouji',
    'show', 'si', 'silk', 'sina', 'singles', 'site', 'sj', 'sk', 'ski', 'skin',
    'sky', 'skype', 'sl', 'sling', 'sm', 'smart', 'smile', 'sn', 'sncf', 'so',
    'soccer', 'social', 'softbank', 'software', 'sohu', 'solar', 'solutions',
    'song', 'sony', 'soy', 'spa', 'space', 'sport', 'spot', 'sr', 'srl', 'ss',
    'st', 'stada', 'staples', 'star', 'statebank', 'statefarm', 'stc', 'stcgroup',
    'stockholm', 'storage', 'store', 'stream', 'studio', 'study', 'style', 'su',
    'sucks', 'supplies', 'supply', 'support', 'surf', 'surgery', 'suzuki', 'sv',
    'swatch', 'swiss', 'sx', 'sy', 'sydney', 'systems', 'sz', 'tab', 'taipei',
    'talk', 'taobao', 'target', 'tatamotors', 'tatar', 'tattoo', 'tax', 'taxi',
    'tc', 'tci', 'td', 'tdk', 'team', 'tech', 'technology', 'tel', 'temasek',
    'tennis', 'teva', 'tf', 'tg', 'th', 'thd', 'theater', 'theatre', 'tiaa',
    'tickets', 'tienda', 'tips', 'tires', 'tirol', 'tj', 'tjmaxx', 'tjx', 'tk',
    'tkmaxx', 'tl', 'tm', 'tmall', 'tn', 'to', 'today', 'tokyo', 'tools', 'top',
    'toray', 'toshiba', 'total', 'tours', 'town', 'toyota', 'toys', 'tr', 'trade',
    'trading', 'training', 'travel', 'travelers', 'travelersinsurance', 'trust',
    'trv', 'tt', 'tube', 'tui', 'tunes', 'tushu', 'tv', 'tvs', 'tw', 'tz', 'ua',
    'ubank', 'ubs', 'ug', 'uk', 'unicom', 'university', 'uno', 'uol', 'ups', 'us',
    'uy', 'uz', 'va', 'vacations', 'vana', 'vanguard', 'vc', 've', 'vegas',
    'ventures', 'verisign', 'versicherung', 'vet', 'vg', 'vi', 'viajes', 'video',
    'vig', 'viking', 'villas', 'vin', 'vip', 'virgin', 'visa', 'vision', 'viva',
    'vivo', 'vlaanderen', 'vn', 'vodka', 'volvo', 'vote', 'voting', 'voto',
    'voyage', 'vu', 'wales', 'walmart', 'walter', 'wang', 'wanggou', 'watch',
    'watches', 'weather', 'weatherchannel', 'webcam', 'weber', 'website', 'wed',
    'wedding', 'weibo', 'weir', 'wf', 'whoswho', 'wien', 'wiki', 'williamhill',
    'win', 'windows', 'wine', 'winners', 'wme', 'wolterskluwer', 'woodside',
    'work', 'works', 'world', 'wow', 'ws', 'wtc', 'wtf', 'xbox', 'xerox', 'xihuan',
    'xin', 'xn--11b4c3d', 'xn--1ck2e1b', 'xn--1qqw23a', 'xn--2scrj9c',
    'xn--30rr7y', 'xn--3bst00m', 'xn--3ds443g', 'xn--3e0b707e', 'xn--3hcrj9c',
    'xn--3pxu8k', 'xn--42c2d9a', 'xn--45br5cyl', 'xn--45brj9c', 'xn--45q11c',
    'xn--4dbrk0ce', 'xn--4gbrim', 'xn--54b7fta0cc', 'xn--55qw42g', 'xn--55qx5d',
    'xn--5su34j936bgsg', 'xn--5tzm5g', 'xn--6frz82g', 'xn--6qq986b3xl',
    'xn--80adxhks', 'xn--80ao21a', 'xn--80aqecdr1a', 'xn--80asehdb', 'xn--80aswg',
    'xn--8y0a063a', 'xn--90a3ac', 'xn--90ae', 'xn--90ais', 'xn--9dbq2a',
    'xn--9et52u', 'xn--9krt00a', 'xn--b4w605ferd', 'xn--bck1b9a5dre4c',
    'xn--c1avg', 'xn--c2br7g', 'xn--cck2b3b', 'xn--cckwcxetd', 'xn--cg4bki',
    'xn--clchc0ea0b2g2a9gcd', 'xn--czr694b', 'xn--czrs0t', 'xn--czru2d',
    'xn--d1acj3b', 'xn--d1alf', 'xn--e1a4c', 'xn--eckvdtc9d', 'xn--efvy88h',
    'xn--fct429k', 'xn--fhbei', 'xn--fiq228c5hs', 'xn--fiq64b', 'xn--fiqs8s',
    'xn--fiqz9s', 'xn--fjq720a', 'xn--flw351e', 'xn--fpcrj9c3d', 'xn--fzc2c9e2c',
    'xn--fzys8d69uvgm', 'xn--g2xx48c', 'xn--gckr3f0f', 'xn--gecrj9c',
    'xn--gk3at1e', 'xn--h2breg3eve', 'xn--h2brj9c', 'xn--h2brj9c8c', 'xn--hxt814e',
    'xn--i1b6b1a6a2e', 'xn--imr513n', 'xn--io0a7i', 'xn--j1aef', 'xn--j1amh',
    'xn--j6w193g', 'xn--jlq480n2rg', 'xn--jvr189m', 'xn--kcrx77d1x4a',
    'xn--kprw13d', 'xn--kpry57d', 'xn--kput3i', 'xn--l1acc', 'xn--lgbbat1ad8j',
    'xn--mgb9awbf', 'xn--mgba3a3ejt', 'xn--mgba3a4f16a', 'xn--mgba7c0bbn0a',
    'xn--mgbaam7a8h', 'xn--mgbab2bd', 'xn--mgbah1a3hjkrd', 'xn--mgbai9azgqp6j',
    'xn--mgbayh7gpa', 'xn--mgbbh1a', 'xn--mgbbh1a71e', 'xn--mgbc0a9azcg',
    'xn--mgbca7dzdo', 'xn--mgbcpq6gpa1a', 'xn--mgberp4a5d4ar', 'xn--mgbgu82a',
    'xn--mgbi4ecexp', 'xn--mgbpl2fh', 'xn--mgbt3dhd', 'xn--mgbtx2b',
    'xn--mgbx4cd0ab', 'xn--mix891f', 'xn--mk1bu44c', 'xn--mxtq1m', 'xn--ngbc5azd',
    'xn--ngbe9e0a', 'xn--ngbrx', 'xn--node', 'xn--nqv7f', 'xn--nqv7fs00ema',
    'xn--nyqy26a', 'xn--o3cw4h', 'xn--ogbpf8fl', 'xn--otu796d', 'xn--p1acf',
    'xn--p1ai', 'xn--pgbs0dh', 'xn--pssy2u', 'xn--q7ce6a', 'xn--q9jyb4c',
    'xn--qcka1pmc', 'xn--qxa6a', 'xn--qxam', 'xn--rhqv96g', 'xn--rovu88b',
    'xn--rvc1e0am3e', 'xn--s9brj9c', 'xn--ses554g', 'xn--t60b56a', 'xn--tckwe',
    'xn--tiq49xqyj', 'xn--unup4y', 'xn--vermgensberater-ctb',
    'xn--vermgensberatung-pwb', 'xn--vhquv', 'xn--vuq861b', 'xn--w4r85el8fhu5dnra',
    'xn--w4rs40l', 'xn--wgbh1c', 'xn--wgbl6a', 'xn--xhq521b', 'xn--xkc2al3hye2a',
    'xn--xkc2dl3a5ee0h', 'xn--y9a3aq', 'xn--yfro4i67o', 'xn--ygbi2ammx',
    'xn--zfr164b', 'xxx', 'xyz', 'yachts', 'yahoo', 'yamaxun', 'yandex', 'ye',
    'yodobashi', 'yoga', 'yokohama', 'you', 'youtube', 'yt', 'yun', 'za', 'zappos',
    'zara', 'zero', 'zip', 'zm', 'zone', 'zuerich', 'zw'
}




def main():
    args = get_args()
    greplinks(args)



def get_args():
    Usage = """Basic usage: ./greplinks -i inputfile -o outfile \n
    \r cat inputfile | ./greplinks -o output_file"""

    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            print(Usage)
            sys.stderr.write("error: %s\n" % message)
            self.print_help()
            os._exit(2)

    def args_parser():
        msg = f"""\033[1;31mThis tool is developed by Arshia Mashhoor
        \runder MIT Open source LICENCE for educational usgae only.
        \rAuthor is not responsible for any abuse!\033[0m\n{'Help':*^100}"""

        parser = MyParser(
            formatter_class=argparse.RawTextHelpFormatter,
            prog="greplinks",
            description=msg,
            epilog=textwrap.dedent(
                f"""\
                    \r{'About':-^100}
                    \nAuthor: Arshia Mashhoor
                    \nGithub:https://github.com/a-mashhoor/greplinks
                """
            ),
            add_help=True,
        )

        input_group = parser.add_mutually_exclusive_group(required=False)
        input_group.add_argument(
            "-i",
            "--input-file",
            nargs=1,
            type=argparse.FileType("r", encoding="UTF-8"),
            help="read a input file",
        )

        parser.add_argument(
            "-s",
            "--silent",
            action=argparse.BooleanOptionalAction,
            default=False,
            help="prints nothing on stdout",
        )


        parser.add_argument(
            "-v",
            "--verbose",
            action=argparse.BooleanOptionalAction,
            default=False,
            help="verbose mode",
        )

        parser.add_argument(
            "-c",
            "--colored",
            action=argparse.BooleanOptionalAction,
            default=False,
            help="colorize the output on stdout",
        )

        parser.add_argument(
            "-so",
            "--sort",
            action=argparse.BooleanOptionalAction,
            default=False,
            help="sorts the output default False",
        )

        parser.add_argument(
            "-t",
            "--threads",
            type=int,
            default=25,
            help="number of threads to use for URL validation (default: 25)"
        )

        output_group = parser.add_mutually_exclusive_group(required=False)
        output_group.add_argument(
            "-o",
            "--output",
            nargs=1,
            type=argparse.FileType("w", encoding="UTF-8"),
            help="save output in text (ascii based) file",
        )

        parser.add_argument(
            "-V", "--version", action="version", version="%(prog)s 1.0.0"
        )

        args = parser.parse_args()
        return args

    return args_parser()


def print_colored(text, color="green"):
    colors = {"green": "\033[92m", "red": "\033[91m", "reset": "\033[0m"}
    print(f"{colors[color]}{text}{colors['reset']}")


def is_valid_ipv4(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False


def is_valid_ipv6(ip):
    try:
        ipaddress.IPv6Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False


def is_connected():
    """Check if there's an internet connection by pinging Cloudflare DNS."""
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=2)
        return True
    except OSError:
        return False


def fetch_tlds_from_iana():
    """Fetch TLDs from IANA or use cached file or fallback list."""
    if os.path.exists(TLD_CACHE_PATH):
        try:
            with open(TLD_CACHE_PATH, "r", encoding="utf-8") as f:
                return set(line.strip().lower() for line in f if line)
        except Exception:
            pass

    if is_connected():
        try:
            with urllib.request.urlopen(
                "https://data.iana.org/TLD/tlds-alpha-by-domain.txt", timeout=5
            ) as response:
                lines = response.read().decode("utf-8").splitlines()
                tlds = set(
                    line.strip().lower()
                    for line in lines
                    if line and not line.startswith("#")
                )
                with open(TLD_CACHE_PATH, "w", encoding="utf-8") as f:
                    for tld in sorted(tlds):
                        f.write(tld + "\n")
                return tlds
        except Exception:
            pass

    return FALLBACK_TLDS


VALID_TLDS = fetch_tlds_from_iana()


def has_valid_tld(domain: str) -> bool:
    """Check if domain has a valid TLD."""
    if "." not in domain:
        return False
    tld = domain.rsplit(".", 1)[-1].lower()
    return tld in VALID_TLDS


def is_valid_url(url):
    """Simplified URL validation that's more permissive."""
    try:
        if not url or len(url) < 3:
            return False

        result = urlparse(url)

        if not result.scheme and not result.netloc:
            if '/' in url:
                domain_part = url.split('/')[0]
            else:
                domain_part = url

            if ':' in domain_part:
                parts = domain_part.rsplit(':', 1)
                if len(parts) == 2:
                    host, port = parts
                    try:
                        port_num = int(port)
                        if not (0 <= port_num <= 65535):
                            return False
                    except ValueError:
                        return False
                else:
                    host = domain_part
            else:
                host = domain_part

            if is_valid_ipv4(host) or is_valid_ipv6(host):
                return True
            elif '.' in host and has_valid_tld(host):
                return True
            else:
                return False

        if result.scheme and result.netloc:
            host = result.netloc.split('@')[-1]  # Remove auth if present
            host = host.split(':')[0]  # Remove port

            if host.startswith('[') and host.endswith(']'):
                host = host[1:-1]

            if is_valid_ipv4(host) or is_valid_ipv6(host):
                return True
            elif has_valid_tld(host):
                return True
            elif host == 'localhost':
                return True
            else:
                return False

        return False

    except Exception:
        return False


def clean_and_prepare_urls(matches):
    """Clean URL matches and prepare them for validation."""
    cleaned_urls = []
    for match in matches:
        cleaned_url = match.strip()

        cleaned_url = re.sub(r'[.,;!?)\]}<>"\']+$', '', cleaned_url)

        if len(cleaned_url) < 4:
            continue

        cleaned_urls.append(cleaned_url)

    return cleaned_urls


def validate_urls_parallel(urls_to_validate, num_threads, v=False):
    """Validate URLs in parallel using threading."""
    valid_urls = []
    seen_urls = set()

    seen_lock = threading.Lock()

    def validate_batch(url_batch):
        batch_results = []
        for url in url_batch:
            with seen_lock:
                if url in seen_urls:
                    continue
                seen_urls.add(url)

            if is_valid_url(url):
                batch_results.append(url)
        return batch_results

    # Split URLs into batches for parallel processing
    batch_size = max(1, len(urls_to_validate) // num_threads)
    url_batches = []
    for i in range(0, len(urls_to_validate), batch_size):
        url_batches.append(urls_to_validate[i:i + batch_size])

    # Process batches in parallel
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(validate_batch, batch) for batch in url_batches]

        for future in as_completed(futures):
            try:
                batch_results = future.result()
                valid_urls.extend(batch_results)
            except Exception as e:
                if v:
                    print(f"Error in batch processing: {e}", file=sys.stderr)

    return valid_urls


def greplinks(args):
    file_path = args.input_file
    output_file = args.output
    silent = args.silent
    verbose = args.verbose
    colored = args.colored
    sort = args.sort
    num_threads = args.threads

    url_regex = re.compile(
        r"\b(?:https?://|wss?://|ws?://|ftp://|sftp://|scp://|tftp://|imap://|imaps://|pop://|pops://|smtp://|smtps://|rtsp://|rtsps://|rtp://|rtmp://|rtmps://|sip://|sips://|jdbc:|odbc:|mongodb://|postgres://|postgresql://|magnet:|bittorrent:|git://|ssh://|svn://|telnet://|irc://|ircs://|data:|ldap://|ldaps://|nfs://|dns://|slack://|zoommtg://|steam://|spotify:|file://)?"
        r"(?:[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|localhost|\[?[0-9a-fA-F:.]+\]?|[0-9]{1,3}(?:\.[0-9]{1,3}){3})"
        r"(?::[0-9]+)?"
        r"(?:/[^\s]*)?\b"
    )

    if file_path:
        text = file_path[0].read()
    else:
        text = sys.stdin.read()

    if verbose:
        print(f"Processing input text ({len(text)} characters)...", file=sys.stderr)

    matches = url_regex.findall(text)

    if verbose:
        print(f"Found {len(matches)} potential URLs with regex", file=sys.stderr)

    cleaned_urls = clean_and_prepare_urls(matches)

    if verbose:
        print(f"After cleaning: {len(cleaned_urls)} URLs to validate", file=sys.stderr)
        print(f"Using {num_threads} threads for validation...", file=sys.stderr)

    valid_urls = validate_urls_parallel(cleaned_urls, num_threads, verbose)

    if verbose:
        print(f"Validation complete. Found {len(valid_urls)} valid URLs", file=sys.stderr)

    final_urls = []
    seen = set()

    for url in valid_urls:
        if url not in seen:
            seen.add(url)
            final_urls.append(url)

    if sort:
        final_urls.sort()

    if output_file:
        for url in final_urls:
            output_file[0].write(url + "\n")
        if verbose:
            print(f"Output written to {output_file[0].name}", file=sys.stderr)

    if not silent:
        for url in final_urls:
            if colored:
                print_colored(url, color="green")
            else:
                print(url)


if __name__ == "__main__":
    main()
