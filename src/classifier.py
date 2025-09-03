import re
from typing import Dict, Optional

class ContentClassifier:
    def __init__(self):
        # Keywords for different categories
        self.category_keywords = {
            'Fashion Business': [
                'revenue', 'sales', 'profit', 'earnings', 'IPO', 'acquisition', 'merger',
                'CEO', 'CFO', 'executive', 'investment', 'funding', 'valuation',
                'market share', 'business', 'company', 'corporation', 'financial',
                'strategy', 'expansion', 'growth', 'partnership', 'collaboration',
                'retail strategy', 'digital transformation', 'supply chain',
                'manufacturing', 'production', 'factory', 'sustainability report'
            ],
            
            'Beauty': [
                'makeup', 'cosmetics', 'skincare', 'beauty', 'lipstick', 'foundation',
                'mascara', 'eyeshadow', 'blush', 'concealer', 'serum', 'moisturizer',
                'cleanser', 'toner', 'sunscreen', 'SPF', 'anti-aging', 'wrinkle',
                'acne', 'skincare routine', 'beauty tips', 'beauty trends',
                'fragrance', 'perfume', 'cologne', 'scent', 'nail polish',
                'manicure', 'pedicure', 'hair care', 'shampoo', 'conditioner'
            ],
            
            'Luxury': [
                'luxury', 'haute couture', 'high-end', 'premium', 'exclusive',
                'limited edition', 'bespoke', 'artisan', 'craftsmanship',
                'Hermès', 'Chanel', 'Louis Vuitton', 'Gucci', 'Prada', 'Dior',
                'Burberry', 'Cartier', 'Tiffany', 'Rolex', 'luxury goods',
                'luxury market', 'affluent', 'ultra-high-net-worth', 'UHNW',
                'luxury experience', 'concierge', 'VIP', 'private shopping'
            ],
            
            'Retail': [
                'retail', 'store', 'shopping', 'mall', 'outlet', 'flagship',
                'pop-up', 'brick-and-mortar', 'physical store', 'retail space',
                'customer experience', 'in-store', 'merchandising', 'inventory',
                'point of sale', 'POS', 'cashier', 'checkout', 'shopping center',
                'department store', 'boutique', 'showroom', 'retail technology',
                'RFID', 'smart fitting room', 'retail analytics', 'foot traffic'
            ],
            
            'E-commerce': [
                'e-commerce', 'ecommerce', 'online shopping', 'digital', 'website',
                'mobile app', 'app', 'online store', 'marketplace', 'Amazon',
                'Shopify', 'direct-to-consumer', 'D2C', 'DTC', 'omnichannel',
                'click-and-collect', 'buy online pick up in store', 'BOPIS',
                'shipping', 'delivery', 'fulfillment', 'logistics', 'warehouse',
                'last mile', 'subscription', 'personalization', 'AI', 'AR', 'VR',
                'social commerce', 'influencer marketing', 'conversion rate',
                'SEO', 'SEM', 'digital marketing', 'performance marketing'
            ],
            
            'Fashion Trends': [
                'trend', 'trending', 'fashion week', 'runway', 'collection',
                'designer', 'style', 'outfit', 'look', 'fashion', 'seasonal',
                'spring', 'summer', 'fall', 'winter', 'resort', 'pre-fall',
                'streetwear', 'athleisure', 'sustainable fashion', 'eco-friendly',
                'vintage', 'retro', 'minimalist', 'maximalist', 'boho', 'grunge',
                'preppy', 'casual', 'formal', 'evening wear', 'red carpet',
                'celebrity style', 'fashion influencer', 'styling tips'
            ]
        }
        
        # Compile regex patterns for efficiency
        self.category_patterns = {}
        for category, keywords in self.category_keywords.items():
            pattern = r'\b(?:' + '|'.join(re.escape(keyword) for keyword in keywords) + r')\b'
            self.category_patterns[category] = re.compile(pattern, re.IGNORECASE)
    
    def classify_article(self, title: str, description: str = '') -> str:
        """Classify article based on title and description"""
        text = f"{title} {description or ''}"
        
        category_scores = {}
        
        for category, pattern in self.category_patterns.items():
            matches = pattern.findall(text)
            category_scores[category] = len(matches)
        
        # Return category with highest score
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category
        
        # Fallback: simple heuristics based on source patterns
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['business', 'financial', 'earnings', 'revenue']):
            return 'Fashion Business'
        elif any(word in text_lower for word in ['beauty', 'makeup', 'skincare']):
            return 'Beauty'
        elif any(word in text_lower for word in ['luxury', 'haute', 'premium']):
            return 'Luxury'
        elif any(word in text_lower for word in ['ecommerce', 'online', 'digital']):
            return 'E-commerce'
        elif any(word in text_lower for word in ['retail', 'store', 'shopping']):
            return 'Retail'
        else:
            return 'Fashion Trends'  # Default category
    
    def get_categories(self) -> list:
        """Get list of available categories"""
        return list(self.category_keywords.keys())
    
    def add_keywords(self, category: str, keywords: list):
        """Add keywords to existing category"""
        if category in self.category_keywords:
            self.category_keywords[category].extend(keywords)
            # Recompile pattern
            pattern = r'\b(?:' + '|'.join(re.escape(keyword) for keyword in self.category_keywords[category]) + r')\b'
            self.category_patterns[category] = re.compile(pattern, re.IGNORECASE)