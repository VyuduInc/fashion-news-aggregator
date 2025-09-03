# Fashion & Beauty RSS Feed URLs
FEED_SOURCES = {
    # Tier 1 - Major International Publications
    'Vogue': 'https://www.vogue.com/feed/rss',
    'WWD': 'https://wwd.com/feed/',
    'Business of Fashion': 'https://www.businessoffashion.com/feed/',
    'Harper\'s Bazaar': 'https://www.harpersbazaar.com/rss/all.xml/',
    'Elle': 'https://www.elle.com/rss/all.xml/',
    'Marie Claire': 'https://www.marieclaire.com/rss/all.xml/',
    'Fashionista': 'https://fashionista.com/feed',
    'Glossy': 'https://glossy.co/feed/',
    'Allure': 'https://www.allure.com/feed/rss',
    'InStyle': 'https://www.instyle.com/syndication/rss',
    
    # Tier 2 - Regional Vogue & Major Publications  
    'Vogue UK': 'https://www.vogue.co.uk/rss',
    'Vogue Paris': 'https://www.vogue.fr/rss',
    'Vogue Italia': 'https://www.vogue.it/rss/all',
    'Grazia': 'https://graziamagazine.com/feed/',
    'Stylist': 'https://www.stylist.co.uk/feed',
    'Refinery29': 'https://www.refinery29.com/rss.xml',
    'Who What Wear': 'https://www.whowhatwear.com/rss',
    'Hypebeast': 'https://hypebeast.com/feed',
    'Highsnobiety': 'https://www.highsnobiety.com/feed/',
    'Fashion Network': 'https://www.fashionnetwork.com/rss/',
    
    # Tier 3 - Beauty Specialists & Trade Publications
    'Beauty Independent': 'https://www.beautyindependent.com/feed/',
    'Retail Dive': 'https://www.retaildive.com/feeds/news/',
    'Modern Retail': 'https://www.modernretail.co/feed/',
    'Drapers': 'https://www.drapersonline.com/rss',
    'Fashion United': 'https://fashionunited.com/rss/news',
    'Fashion Head': 'https://www.fashionhead.com/feed',
    
    # Additional International Sources
    'Vogue Germany': 'https://www.vogue.de/rss/alle',
    'Vogue Spain': 'https://www.vogue.es/rss',
    'Vogue Australia': 'https://www.vogue.com.au/rss',
    'Vogue India': 'https://www.vogue.in/rss',
    'Cosmopolitan': 'https://www.cosmopolitan.com/rss/all.xml/',
    'Teen Vogue': 'https://www.teenvogue.com/feed/rss',
    
    # Beauty-Focused Publications
    'Byrdie': 'https://www.byrdie.com/rss',
    'Into The Gloss': 'https://intothegloss.com/feed/',
    'Beautylish': 'https://www.beautylish.com/rss/articles',
    'Temptalia': 'https://www.temptalia.com/feed/',
    'Makeup and Beauty Blog': 'https://www.makeupandbeautyblog.com/feed/',
    
    # Industry Trade Publications
    'Retail TouchPoints': 'https://www.retailtouchpoints.com/rss.xml',
    'Chain Store Age': 'https://chainstoreage.com/rss.xml',
    'Sourcing Journal': 'https://sourcingjournal.com/feed/',
    'Fashion Dive': 'https://www.fashiondive.com/feeds/news/',
    'Glossy Beauty': 'https://glossy.co/beauty/feed/',
    
    # Sustainable & Tech-Focused Fashion
    'Fashion Revolution': 'https://www.fashionrevolution.org/feed/',
    'Eco-Age': 'https://eco-age.com/feed/',
    'Fashion for Good': 'https://fashionforgood.com/feed/',
    'The Business of Fashion Tech': 'https://www.businessoffashion.com/tags/technology/feed/',
    
    # Luxury Focus
    'Luxury Society': 'https://www.luxurysociety.com/en/rss',
    'Jing Daily': 'https://jingdaily.com/feed/',
    'Luxury Daily': 'https://www.luxurydaily.com/feed/',
    
    # Regional Asian Publications
    'Harper\'s Bazaar Singapore': 'https://harpersbazaar.com.sg/rss.xml',
    'Elle Japan': 'https://www.elle.com/jp/rss/',
    'Vogue Japan': 'https://www.vogue.co.jp/rss',
    
    # Street Style & Culture
    'The Cut': 'https://www.thecut.com/rss.xml',
    'Man Repeller': 'https://repeller.com/feed/',
    'Fashionista Street Style': 'https://fashionista.com/category/street-style/feed'
}

def get_all_feeds():
    """Return all RSS feed URLs"""
    return FEED_SOURCES

def get_feeds_by_category():
    """Return feeds organized by category"""
    return {
        'tier_1_major': {k: v for k, v in list(FEED_SOURCES.items())[:10]},
        'tier_2_regional': {k: v for k, v in list(FEED_SOURCES.items())[10:20]},
        'tier_3_specialty': {k: v for k, v in list(FEED_SOURCES.items())[20:]}
    }