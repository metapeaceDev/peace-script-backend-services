"""
Wardrobe System Models
เสื้อผ้า เครื่องแต่งกาย และเครื่องประดับสำหรับตัวละคร
STEP 3.5 Enhancement - Character Wardrobe & Styling
"""

from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
import uuid

from pydantic import BaseModel, Field


# =============================================================================
# ENUMS - Classification System
# =============================================================================

class ClothingType(str, Enum):
    """ประเภทเสื้อผ้า (100+ types)"""
    
    # === เสื้อส่วนบน (Top Wear) ===
    # เสื้อทั่วไป
    T_SHIRT = "t_shirt"                    # เสื้อยืด
    POLO_SHIRT = "polo_shirt"              # เสื้อโปโล
    DRESS_SHIRT = "dress_shirt"            # เสื้อเชิ้ต
    BLOUSE = "blouse"                      # เสื้อเชิ้ตผู้หญิง
    TANK_TOP = "tank_top"                  # เสื้อกล้าม
    CAMISOLE = "camisole"                  # เสื้อสายเดี่ยว
    CROP_TOP = "crop_top"                  # เสื้อครอป
    TUBE_TOP = "tube_top"                  # เสื้อทรงท่อ
    
    # เสื้อยาว
    LONG_SLEEVE_TOP = "long_sleeve_top"    # เสื้อแขนยาว
    TURTLENECK = "turtleneck"              # เสื้อคอเต่า
    
    # เสื้อคลุม
    SWEATER = "sweater"                    # เสื้อสเวตเตอร์
    CARDIGAN = "cardigan"                  # เสื้อคาร์ดิแกน
    HOODIE = "hoodie"                      # เสื้อฮู้ด
    SWEATSHIRT = "sweatshirt"              # เสื้อสเวตเชิ้ต
    
    # แจ็คเก็ต
    JACKET = "jacket"                      # แจ็คเก็ตทั่วไป
    LEATHER_JACKET = "leather_jacket"      # แจ็คเก็ตหนัง
    DENIM_JACKET = "denim_jacket"          # แจ็คเก็ตยีนส์
    BOMBER_JACKET = "bomber_jacket"        # แจ็คเก็ตบอมเบอร์
    BLAZER = "blazer"                      # เสื้อเบลเซอร์
    
    # โค้ท
    COAT = "coat"                          # โค้ททั่วไป
    TRENCH_COAT = "trench_coat"            # โค้ทยาว
    PEACOAT = "peacoat"                    # โค้ทสั้น
    OVERCOAT = "overcoat"                  # โอเวอร์โค้ท
    PARKA = "parka"                        # เสื้อพาร์ก้า
    
    # === ชุดเดรส (Dresses) ===
    MINI_DRESS = "mini_dress"              # เดรสสั้น
    MIDI_DRESS = "midi_dress"              # เดรสยาวปานกลาง
    MAXI_DRESS = "maxi_dress"              # เดรสยาว
    COCKTAIL_DRESS = "cocktail_dress"      # เดรสค็อกเทล
    EVENING_GOWN = "evening_gown"          # เดรสราตรี
    SUNDRESS = "sundress"                  # เดรสชายหาด
    SHIRT_DRESS = "shirt_dress"            # เดรสเชิ้ต
    WRAP_DRESS = "wrap_dress"              # เดรสผูก
    
    # === เสื้อส่วนล่าง (Bottom Wear) ===
    # กางเกงยีนส์
    JEANS = "jeans"                        # กางเกงยีนส์
    SKINNY_JEANS = "skinny_jeans"          # ยีนส์สกินนี่
    BOYFRIEND_JEANS = "boyfriend_jeans"    # ยีนส์บอยเฟรนด์
    
    # กางเกงขายาว
    DRESS_PANTS = "dress_pants"            # กางเกงสแล็ค
    CHINOS = "chinos"                      # กางเกงชิโน
    CARGO_PANTS = "cargo_pants"            # กางเกงคาร์โก้
    JOGGERS = "joggers"                    # กางเกงขาจั๊ม
    LEGGINGS = "leggings"                  # กางเกงรัดรูป
    
    # กางเกงขาสั้น
    SHORTS = "shorts"                      # กางเกงขาสั้น
    DENIM_SHORTS = "denim_shorts"          # กางเกงยีนส์ขาสั้น
    SPORT_SHORTS = "sport_shorts"          # กางเกงกีฬาขาสั้น
    BERMUDA_SHORTS = "bermuda_shorts"      # กางเกงเบอร์มิวด้า
    
    # กระโปรง
    MINI_SKIRT = "mini_skirt"              # กระโปรงสั้น
    MIDI_SKIRT = "midi_skirt"              # กระโปรงปานกลาง
    MAXI_SKIRT = "maxi_skirt"              # กระโปรงยาว
    A_LINE_SKIRT = "a_line_skirt"          # กระโปรงทรงเอ
    PENCIL_SKIRT = "pencil_skirt"          # กระโปรงเพนซิล
    PLEATED_SKIRT = "pleated_skirt"        # กระโปรงพลีท
    
    # === รองเท้า (Footwear) ===
    # รองเท้าหนัง
    OXFORD_SHOES = "oxford_shoes"          # รองเท้าออกฟอร์ด
    DERBY_SHOES = "derby_shoes"            # รองเท้าเดอร์บี้
    LOAFERS = "loafers"                    # รองเท้าโลฟเฟอร์
    
    # รองเท้าผ้าใบ
    SNEAKERS = "sneakers"                  # รองเท้าผ้าใบ
    RUNNING_SHOES = "running_shoes"        # รองเท้าวิ่ง
    BASKETBALL_SHOES = "basketball_shoes"  # รองเท้าบาสเกตบอล
    
    # รองเท้าผู้หญิง
    HEELS = "heels"                        # รองเท้าส้นสูง
    STILETTO = "stiletto"                  # ส้นเข็ม
    WEDGE = "wedge"                        # ส้นเตารีด
    FLATS = "flats"                        # รองเท้าแฟลต
    BALLET_FLATS = "ballet_flats"          # บัลเล่ต์แฟลต
    
    # รองเท้าบู๊ท
    BOOTS = "boots"                        # รองเท้าบู๊ท
    ANKLE_BOOTS = "ankle_boots"            # บู๊ทสั้น
    KNEE_HIGH_BOOTS = "knee_high_boots"    # บู๊ทยาว
    
    # รองเท้าสบายๆ
    SANDALS = "sandals"                    # รองเท้าแตะ
    FLIP_FLOPS = "flip_flops"              # รองเท้าแตะหนีบ
    SLIPPERS = "slippers"                  # รองเท้าแตะในบ้าน
    
    # === หมวก (Headwear) ===
    CAP = "cap"                            # หมวกแก๊ป
    BEANIE = "beanie"                      # หมวกบีนนี่
    FEDORA = "fedora"                      # หมวกเฟดอร่า
    BUCKET_HAT = "bucket_hat"              # หมวกบัคเก็ต
    WIDE_BRIM_HAT = "wide_brim_hat"        # หมวกปีกกว้าง
    STRAW_HAT = "straw_hat"                # หมวกฟาง
    
    # === ชุดชั้นในและชุดนอน ===
    UNDERWEAR = "underwear"                # ชุดชั้นใน
    UNDERSHIRT = "undershirt"              # เสื้อชั้นใน
    PAJAMAS = "pajamas"                    # ชุดนอน
    NIGHTGOWN = "nightgown"                # ชุดนอนกระโปรง
    ROBE = "robe"                          # เสื้อคลุมนอน
    
    # === ชุดกีฬา ===
    SPORT_JERSEY = "sport_jersey"          # เสื้อกีฬา
    YOGA_PANTS = "yoga_pants"              # กางเกงโยคะ
    SWIMSUIT = "swimsuit"                  # ชุดว่ายน้ำ
    BIKINI = "bikini"                      # บิกินี่
    SWIM_TRUNKS = "swim_trunks"            # กางเกงว่ายน้ำ
    
    # === ชุดพิเศษ ===
    SUIT_JACKET = "suit_jacket"            # เสื้อสูท
    SUIT_PANTS = "suit_pants"              # กางเกงสูท
    VEST = "vest"                          # เสื้อกั๊ก
    TUXEDO = "tuxedo"                      # ชุดทักซิโด้
    TRADITIONAL_THAI = "traditional_thai"  # ชุดไทย
    UNIFORM = "uniform"                    # ชุดยูนิฟอร์ม
    COSTUME = "costume"                    # ชุดคอสเพลย์


class ClothingCategory(str, Enum):
    """หมวดหมู่หลักเสื้อผ้า"""
    TOP_WEAR = "top_wear"              # เสื้อส่วนบน
    BOTTOM_WEAR = "bottom_wear"        # เสื้อส่วนล่าง
    FULL_OUTFIT = "full_outfit"        # ชุดเต็มตัว (เดรส, ชุดสูท)
    FOOTWEAR = "footwear"              # รองเท้า
    HEADWEAR = "headwear"              # หมวก
    UNDERWEAR = "underwear"            # ชุดชั้นใน
    SLEEPWEAR = "sleepwear"            # ชุดนอน
    SPORTSWEAR = "sportswear"          # ชุดกีฬา
    SPECIAL_OCCASION = "special"       # ชุดพิเศษ


class AccessoryType(str, Enum):
    """ประเภทเครื่องประดับ"""
    
    # === เครื่องประดับคอ (Neckwear) ===
    NECKLACE = "necklace"                  # สร้อยคอ
    CHOKER = "choker"                      # สร้อยสั้น
    PENDANT = "pendant"                    # จี้
    CHAIN = "chain"                        # สร้อยโซ่
    NECKTIE = "necktie"                    # เนคไท
    BOW_TIE = "bow_tie"                    # เนคไทโบว์
    SCARF = "scarf"                        # ผ้าพันคอ
    
    # === เครื่องประดับมือ (Handwear) ===
    RING = "ring"                          # แหวน
    WEDDING_RING = "wedding_ring"          # แหวนแต่งงาน
    BRACELET = "bracelet"                  # สร้อยข้อมือ
    BANGLE = "bangle"                      # กำไล
    WATCH = "watch"                        # นาฬิกา
    SMART_WATCH = "smart_watch"            # นาฬิกาอัจฉริยะ
    
    # === เครื่องประดับหู (Earwear) ===
    EARRINGS = "earrings"                  # ต่างหู
    STUD_EARRINGS = "stud_earrings"        # ต่างหูติดหู
    HOOP_EARRINGS = "hoop_earrings"        # ต่างหูห่วง
    DROP_EARRINGS = "drop_earrings"        # ต่างหูห้อย
    
    # === กระเป๋า (Bags) ===
    HANDBAG = "handbag"                    # กระเป๋าถือ
    TOTE_BAG = "tote_bag"                  # กระเป๋าโท้ท
    CLUTCH = "clutch"                      # กระเป๋าคลัตช์
    SHOULDER_BAG = "shoulder_bag"          # กระเป๋าสะพาย
    BACKPACK = "backpack"                  # กระเป๋าเป้
    BRIEFCASE = "briefcase"                # กระเป๋าเอกสาร
    MESSENGER_BAG = "messenger_bag"        # กระเป๋าสะพายข้าง
    BELT_BAG = "belt_bag"                  # กระเป๋าคาดเอว
    WALLET = "wallet"                      # กระเป๋าสตางค์
    
    # === แว่นตา (Eyewear) ===
    SUNGLASSES = "sunglasses"              # แว่นกันแดด
    GLASSES = "glasses"                    # แว่นสายตา
    READING_GLASSES = "reading_glasses"    # แว่นอ่านหนังสือ
    
    # === เข็มขัด (Belts) ===
    BELT = "belt"                          # เข็มขัด
    LEATHER_BELT = "leather_belt"          # เข็มขัดหนัง
    CHAIN_BELT = "chain_belt"              # เข็มขัดโซ่
    
    # === อื่นๆ (Other) ===
    BROOCH = "brooch"                      # เข็มกลัด
    TIE_CLIP = "tie_clip"                  # ที่หนีบเนคไท
    CUFFLINKS = "cufflinks"                # กระดุมข้อมือ
    POCKET_SQUARE = "pocket_square"        # ผ้าเช็ดหน้า
    HAIR_ACCESSORY = "hair_accessory"      # เครื่องประดับผม
    SOCKS = "socks"                        # ถุงเท้า
    GLOVES = "gloves"                      # ถุงมือ


class AccessoryCategory(str, Enum):
    """หมวดหมู่เครื่องประดับ"""
    NECKWEAR = "neckwear"              # เครื่องประดับคอ
    HANDWEAR = "handwear"              # เครื่องประดับมือ
    EARWEAR = "earwear"                # เครื่องประดับหู
    BAGS = "bags"                      # กระเป๋า
    EYEWEAR = "eyewear"                # แว่นตา
    BELTS = "belts"                    # เข็มขัด
    OTHER = "other"                    # อื่นๆ


class ClothingStyle(str, Enum):
    """สไตล์เสื้อผ้า"""
    CASUAL = "casual"                  # สบายๆ
    FORMAL = "formal"                  # ทางการ
    BUSINESS = "business"              # ทำงาน
    SPORTY = "sporty"                  # กีฬา
    ELEGANT = "elegant"                # หรูหรา
    VINTAGE = "vintage"                # วินเทจ
    BOHEMIAN = "bohemian"              # โบฮีเมียน
    PUNK = "punk"                      # พังค์
    STREETWEAR = "streetwear"          # สตรีทแวร์
    MINIMALIST = "minimalist"          # มินิมอล
    ROMANTIC = "romantic"              # โรแมนติก
    PREPPY = "preppy"                  # เปรปปี้
    GRUNGE = "grunge"                  # กรันจ์
    ATHLEISURE = "athleisure"          # แอธเลเชอร์


class Season(str, Enum):
    """ฤดูกาล"""
    SPRING = "spring"                  # ฤดูใบไม้ผลิ
    SUMMER = "summer"                  # ฤดูร้อน
    FALL = "fall"                      # ฤดูใบไม้ร่วง
    WINTER = "winter"                  # ฤดูหนาว
    ALL_SEASON = "all_season"          # ทุกฤดู


class Occasion(str, Enum):
    """โอกาสใช้"""
    DAILY = "daily"                    # ใช้ประจำวัน
    WORK = "work"                      # ทำงาน
    CASUAL_OUTING = "casual_outing"    # เที่ยวสบายๆ
    DATE = "date"                      # เดท
    PARTY = "party"                    # งานปาร์ตี้
    FORMAL_EVENT = "formal_event"      # งานทางการ
    WEDDING = "wedding"                # งานแต่งงาน
    SPORT = "sport"                    # ออกกำลังกาย
    BEACH = "beach"                    # ชายหาด
    TRAVEL = "travel"                  # เดินทาง
    SLEEP = "sleep"                    # นอน
    HOME = "home"                      # อยู่บ้าน
    BUSINESS_MEETING = "business"      # ประชุมธุรกิจ
    INTERVIEW = "interview"            # สัมภาษณ์งาน


# =============================================================================
# MODELS - Wardrobe System
# =============================================================================

class ClothingItem(BaseModel):
    """รายการเสื้อผ้า - Clothing Item Model"""
    
    # === Core Identity ===
    item_id: str = Field(
        default_factory=lambda: f"CLO-{uuid.uuid4().hex[:8].upper()}",
        description="รหัสเสื้อผ้า"
    )
    name: str = Field(..., min_length=1, max_length=200, description="ชื่อเสื้อผ้า")
    description: Optional[str] = Field(None, max_length=1000, description="คำอธิบาย")
    
    # === Classification ===
    category: ClothingCategory = Field(..., description="หมวดหมู่หลัก")
    type: ClothingType = Field(..., description="ประเภทเสื้อผ้า")
    style: ClothingStyle = Field(default=ClothingStyle.CASUAL, description="สไตล์")
    
    # === Physical Properties ===
    color: str = Field(..., description="สีหลัก (ชื่อหรือ hex code)")
    secondary_colors: List[str] = Field(
        default_factory=list,
        description="สีรอง (ถ้ามี)"
    )
    material: str = Field(
        ...,
        description="วัสดุ (cotton, silk, denim, leather, polyester, wool, linen, etc.)"
    )
    pattern: Optional[str] = Field(
        None,
        description="ลาย (solid, striped, checkered, floral, polka_dot, plaid, paisley, etc.)"
    )
    
    # === Brand & Value ===
    brand: Optional[str] = Field(None, max_length=100, description="แบรนด์")
    price: Optional[float] = Field(None, ge=0, description="ราคา")
    currency: str = Field(default="THB", description="สกุลเงิน")
    
    # === Size & Fit ===
    size: Optional[str] = Field(
        None,
        description="ไซส์ (XS, S, M, L, XL, XXL, or numeric like 38, 40, etc.)"
    )
    fit: Optional[str] = Field(
        None,
        description="ความพอดี (tight, slim, regular, loose, oversized)"
    )
    
    # === Context ===
    season: List[Season] = Field(
        default_factory=list,
        description="ฤดูกาลที่เหมาะสม"
    )
    occasions: List[Occasion] = Field(
        default_factory=list,
        description="โอกาสที่เหมาะสม"
    )
    
    # === Condition & Usage ===
    condition: str = Field(
        default="new",
        description="สภาพ (new, like_new, good, worn, damaged)"
    )
    purchase_date: Optional[datetime] = Field(None, description="วันที่ซื้อ")
    last_worn: Optional[datetime] = Field(None, description="สวมใส่ครั้งล่าสุด")
    wear_count: int = Field(default=0, ge=0, description="จำนวนครั้งที่สวมใส่")
    
    # === Tags & Notes ===
    tags: List[str] = Field(
        default_factory=list,
        description="แท็กเพิ่มเติม (comfortable, favorite, special, etc.)"
    )
    notes: Optional[str] = Field(None, max_length=500, description="บันทึกเพิ่มเติม")
    
    # === Visual ===
    image_url: Optional[str] = Field(None, description="URL รูปภาพ")
    thumbnail_url: Optional[str] = Field(None, description="URL รูปภาพขนาดเล็ก")
    
    # === Favorites ===
    is_favorite: bool = Field(default=False, description="รายการโปรด")
    favorite_score: float = Field(
        default=5.0,
        ge=0,
        le=10,
        description="คะแนนความชอบ (0-10)"
    )
    
    # === Metadata ===
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="สร้างเมื่อ"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="อัปเดตล่าสุด"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_id": "CLO-A1B2C3D4",
                "name": "เสื้อเชิ้ตสีขาวแขนยาว",
                "description": "เสื้อเชิ้ตผ้าคอตตอน สีขาว แขนยาว เหมาะกับงานทางการ",
                "category": "top_wear",
                "type": "dress_shirt",
                "style": "formal",
                "color": "white",
                "material": "cotton",
                "pattern": "solid",
                "brand": "Uniqlo",
                "price": 990,
                "size": "M",
                "fit": "slim",
                "season": ["all_season"],
                "occasions": ["work", "formal_event"],
                "is_favorite": True,
                "favorite_score": 8.5
            }
        }


class Accessory(BaseModel):
    """เครื่องประดับ - Accessory Model"""
    
    # === Core Identity ===
    accessory_id: str = Field(
        default_factory=lambda: f"ACC-{uuid.uuid4().hex[:8].upper()}",
        description="รหัสเครื่องประดับ"
    )
    name: str = Field(..., min_length=1, max_length=200, description="ชื่อเครื่องประดับ")
    description: Optional[str] = Field(None, max_length=1000, description="คำอธิบาย")
    
    # === Classification ===
    category: AccessoryCategory = Field(..., description="หมวดหมู่")
    type: AccessoryType = Field(..., description="ประเภท")
    style: ClothingStyle = Field(
        default=ClothingStyle.CASUAL,
        description="สไตล์"
    )
    
    # === Physical Properties ===
    color: str = Field(..., description="สีหลัก")
    secondary_colors: List[str] = Field(
        default_factory=list,
        description="สีรอง"
    )
    material: str = Field(
        ...,
        description="วัสดุ (gold, silver, platinum, leather, fabric, plastic, stainless_steel, etc.)"
    )
    
    # === Brand & Value ===
    brand: Optional[str] = Field(None, max_length=100, description="แบรนด์")
    price: Optional[float] = Field(None, ge=0, description="ราคา")
    currency: str = Field(default="THB", description="สกุลเงิน")
    
    # === Special Properties (for specific accessory types) ===
    # For watches
    is_smart_watch: bool = Field(default=False, description="นาฬิกาอัจฉริยะ")
    
    # For jewelry
    gemstone: Optional[str] = Field(None, description="อัญมณี (diamond, ruby, sapphire, etc.)")
    carat: Optional[float] = Field(None, ge=0, description="น้ำหนักกะรัต (สำหรับเพชร/อัญมณี)")
    
    # For bags
    bag_capacity: Optional[str] = Field(
        None,
        description="ความจุ (small, medium, large) สำหรับกระเป๋า"
    )
    
    # === Context ===
    occasions: List[Occasion] = Field(
        default_factory=list,
        description="โอกาสที่เหมาะสม"
    )
    
    # === Condition & Usage ===
    condition: str = Field(
        default="new",
        description="สภาพ (new, like_new, good, worn, damaged)"
    )
    purchase_date: Optional[datetime] = Field(None, description="วันที่ซื้อ")
    last_worn: Optional[datetime] = Field(None, description="ใช้ครั้งล่าสุด")
    wear_count: int = Field(default=0, ge=0, description="จำนวนครั้งที่ใช้")
    
    # === Tags & Notes ===
    tags: List[str] = Field(default_factory=list, description="แท็ก")
    notes: Optional[str] = Field(None, max_length=500, description="บันทึก")
    
    # === Visual ===
    image_url: Optional[str] = Field(None, description="URL รูปภาพ")
    thumbnail_url: Optional[str] = Field(None, description="URL รูปภาพขนาดเล็ก")
    
    # === Favorites ===
    is_favorite: bool = Field(default=False, description="รายการโปรด")
    favorite_score: float = Field(
        default=5.0,
        ge=0,
        le=10,
        description="คะแนนความชอบ (0-10)"
    )
    
    # === Metadata ===
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="สร้างเมื่อ"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="อัปเดตล่าสุด"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "accessory_id": "ACC-E5F6G7H8",
                "name": "นาฬิกาข้อมือ Seiko",
                "description": "นาฬิกาข้อมือผู้ชาย สายหนัง สีน้ำตาล",
                "category": "handwear",
                "type": "watch",
                "style": "business",
                "color": "brown",
                "material": "leather_stainless_steel",
                "brand": "Seiko",
                "price": 8500,
                "occasions": ["work", "formal_event", "date"],
                "is_favorite": True,
                "favorite_score": 9.0
            }
        }


class Outfit(BaseModel):
    """ชุดสำเร็จรูป - Complete Outfit Model"""
    
    # === Core Identity ===
    outfit_id: str = Field(
        default_factory=lambda: f"OUT-{uuid.uuid4().hex[:8].upper()}",
        description="รหัสชุด"
    )
    name: str = Field(..., min_length=1, max_length=200, description="ชื่อชุด")
    description: Optional[str] = Field(None, max_length=1000, description="คำอธิบาย")
    
    # === Components (References to items) ===
    clothing_items: List[str] = Field(
        default_factory=list,
        description="รายการ item_id ของเสื้อผ้า"
    )
    accessories: List[str] = Field(
        default_factory=list,
        description="รายการ accessory_id ของเครื่องประดับ"
    )
    
    # === Classification ===
    style: ClothingStyle = Field(..., description="สไตล์โดยรวม")
    occasion: Occasion = Field(..., description="โอกาสหลัก")
    season: Season = Field(default=Season.ALL_SEASON, description="ฤดูกาล")
    
    # === Color Palette ===
    dominant_colors: List[str] = Field(
        default_factory=list,
        description="สีหลักของชุด"
    )
    
    # === Rating & Usage ===
    rating: float = Field(
        default=5.0,
        ge=0,
        le=10,
        description="คะแนนชุด (0-10)"
    )
    wear_count: int = Field(default=0, ge=0, description="จำนวนครั้งที่สวมใส่")
    last_worn: Optional[datetime] = Field(None, description="สวมใส่ครั้งล่าสุด")
    
    # === Mood & Vibe ===
    mood: Optional[str] = Field(
        None,
        description="อารมณ์ของชุด (confident, romantic, playful, professional, etc.)"
    )
    vibe: Optional[str] = Field(
        None,
        description="บรรยากาศ (elegant, edgy, cozy, fresh, etc.)"
    )
    
    # === Tags & Notes ===
    tags: List[str] = Field(
        default_factory=list,
        description="แท็ก (go-to, power_outfit, date_night, etc.)"
    )
    notes: Optional[str] = Field(None, max_length=500, description="บันทึก")
    
    # === Visual ===
    outfit_image_url: Optional[str] = Field(
        None,
        description="URL รูปภาพชุดรวม (ถ้ามีการถ่ายภาพชุดทั้งหมด)"
    )
    thumbnail_url: Optional[str] = Field(None, description="URL รูปภาพขนาดเล็ก")
    
    # === Favorites ===
    is_favorite: bool = Field(default=False, description="ชุดโปรด")
    
    # === AI Suggestions (Optional) ===
    ai_generated: bool = Field(
        default=False,
        description="สร้างโดย AI outfit recommendation"
    )
    match_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="คะแนนความเข้ากันของชุด (0-100)"
    )
    
    # === Metadata ===
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="สร้างเมื่อ"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="อัปเดตล่าสุด"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "outfit_id": "OUT-I9J0K1L2",
                "name": "ชุดทำงานออฟฟิศ",
                "description": "ชุดทำงานวันธรรมดา สุภาพและเป็นทางการ",
                "clothing_items": ["CLO-12345678", "CLO-87654321", "CLO-11223344"],
                "accessories": ["ACC-55667788", "ACC-99887766"],
                "style": "business",
                "occasion": "work",
                "season": "all_season",
                "dominant_colors": ["white", "black", "brown"],
                "rating": 8.5,
                "mood": "professional",
                "vibe": "confident",
                "is_favorite": True
            }
        }


class WardrobeStats(BaseModel):
    """สถิติตู้เสื้อผ้า"""
    total_clothing: int = Field(default=0, description="จำนวนเสื้อผ้าทั้งหมด")
    total_accessories: int = Field(default=0, description="จำนวนเครื่องประดับทั้งหมด")
    total_outfits: int = Field(default=0, description="จำนวนชุดทั้งหมด")
    
    # By Category
    clothing_by_category: Dict[str, int] = Field(
        default_factory=dict,
        description="จำนวนเสื้อผ้าแยกตามหมวดหมู่"
    )
    accessories_by_category: Dict[str, int] = Field(
        default_factory=dict,
        description="จำนวนเครื่องประดับแยกตามหมวดหมู่"
    )
    
    # By Style
    most_worn_style: Optional[ClothingStyle] = Field(
        default=None,
        description="สไตล์ที่สวมใส่บ่อยที่สุด"
    )
    style_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="การกระจายของสไตล์"
    )
    
    # By Occasion
    outfits_by_occasion: Dict[str, int] = Field(
        default_factory=dict,
        description="จำนวนชุดแยกตามโอกาส"
    )
    
    # Favorites
    favorite_items_count: int = Field(default=0, description="จำนวนรายการโปรด")
    favorite_outfits_count: int = Field(default=0, description="จำนวนชุดโปรด")
    
    # Most Worn
    most_worn_item_id: Optional[str] = Field(default=None, description="เสื้อผ้าที่สวมใส่บ่อยที่สุด")
    most_worn_outfit_id: Optional[str] = Field(default=None, description="ชุดที่สวมใส่บ่อยที่สุด")
    
    # Value
    total_wardrobe_value: float = Field(default=0.0, description="มูลค่ารวมของตู้เสื้อผ้า")
    average_item_value: float = Field(default=0.0, description="มูลค่าเฉลี่ยต่อชิ้น")


class Wardrobe(BaseModel):
    """ตู้เสื้อผ้าของตัวละคร - Character Wardrobe Model"""
    
    # === Owner ===
    character_id: str = Field(..., description="รหัสตัวละคร (model_id or actor_id)")
    character_name: str = Field(..., description="ชื่อตัวละคร")
    
    # === Collections ===
    clothing_collection: List[ClothingItem] = Field(
        default_factory=list,
        description="คอลเลกชั่นเสื้อผ้า"
    )
    accessory_collection: List[Accessory] = Field(
        default_factory=list,
        description="คอลเลกชั่นเครื่องประดับ"
    )
    outfit_collection: List[Outfit] = Field(
        default_factory=list,
        description="คอลเลกชั่นชุดสำเร็จรูป"
    )
    
    # === Current State ===
    current_outfit_id: Optional[str] = Field(
        default=None,
        description="ชุดที่สวมใส่ในปัจจุบัน"
    )
    current_clothing_ids: List[str] = Field(
        default_factory=list,
        description="เสื้อผ้าที่สวมใส่ในปัจจุบัน (ถ้าไม่ใช้ outfit)"
    )
    current_accessory_ids: List[str] = Field(
        default_factory=list,
        description="เครื่องประดับที่สวมใส่ในปัจจุบัน"
    )
    
    # === Statistics ===
    stats: WardrobeStats = Field(
        default_factory=lambda: WardrobeStats(),
        description="สถิติตู้เสื้อผ้า"
    )
    
    # === Preferences ===
    default_style: Optional[ClothingStyle] = Field(
        default=None,
        description="สไตล์เริ่มต้นของตัวละคร"
    )
    favorite_colors: List[str] = Field(
        default_factory=list,
        description="สีที่ชอบ"
    )
    favorite_brands: List[str] = Field(
        default_factory=list,
        description="แบรนด์ที่ชอบ"
    )
    style_preferences: Dict[str, float] = Field(
        default_factory=dict,
        description="ความชอบแยกตามสไตล์ (style_name: score 0-10)"
    )
    
    # === Budget & Shopping ===
    wardrobe_budget: Optional[float] = Field(
        default=None,
        ge=0,
        description="งบประมาณตู้เสื้อผ้า"
    )
    shopping_wishlist: List[str] = Field(
        default_factory=list,
        description="รายการที่อยากซื้อ (item names or descriptions)"
    )
    
    # === Metadata ===
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="สร้างเมื่อ"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="อัปเดตล่าสุด"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "character_id": "peace-mind-001",
                "character_name": "รินรดา",
                "current_outfit_id": "OUT-I9J0K1L2",
                "stats": {
                    "total_clothing": 45,
                    "total_accessories": 18,
                    "total_outfits": 12
                },
                "default_style": "business",
                "favorite_colors": ["white", "black", "navy", "cream"],
                "favorite_brands": ["Uniqlo", "Zara", "COS"]
            }
        }


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    # Enums
    "ClothingType",
    "ClothingCategory",
    "AccessoryType",
    "AccessoryCategory",
    "ClothingStyle",
    "Season",
    "Occasion",
    
    # Models
    "ClothingItem",
    "Accessory",
    "Outfit",
    "WardrobeStats",
    "Wardrobe",
]
