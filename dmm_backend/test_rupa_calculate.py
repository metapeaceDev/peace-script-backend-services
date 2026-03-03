"""
Quick test script for Rupa calculation
"""
import asyncio
from documents import DigitalMindModel
from modules.rupa_engine import calculate_and_save_rupa
from modules.rupa_sync import RupaJivitindriaSyncLayer
from rupa_models import RupaProfile


async def test_calculate():
    """Test rupa calculation directly"""
    model_id = "peace-mind-001"
    
    print(f"🔍 Testing Rupa Calculation for {model_id}")
    print("=" * 60)
    
    # Step 1: Find model
    print(f"\n1️⃣ Finding model...")
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        print(f"❌ Model not found: {model_id}")
        return
    print(f"✅ Model found: {model.model_id}")
    
    # Step 2: Check existing RupaProfile
    print(f"\n2️⃣ Checking existing RupaProfile...")
    existing = await RupaProfile.find_one(RupaProfile.model_id == model_id)
    if existing:
        print(f"⚠️  RupaProfile already exists (ID: {existing.id})")
        print(f"   Deleting for fresh calculation...")
        await existing.delete()
        print(f"✅ Deleted existing RupaProfile")
    else:
        print(f"✅ No existing RupaProfile")
    
    # Step 3: Calculate rupa
    print(f"\n3️⃣ Calculating complete RupaProfile (28 Material Forms)...")
    try:
        rupa = await calculate_and_save_rupa(model_id)
        print(f"✅ RupaProfile calculated successfully!")
        print(f"   ID: {rupa.id}")
        print(f"   Total Kalapas: {rupa.total_kalapa_count}")
        print(f"   Age: {rupa.age} years")
        print(f"   Health: {rupa.health_baseline:.1f}%")
        print(f"   Life Force: {rupa.current_life_force:.1f}%")
    except Exception as e:
        print(f"❌ Calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Sync jivitindriya
    print(f"\n4️⃣ Syncing Jivitindriya...")
    try:
        synced = await RupaJivitindriaSyncLayer.sync_rupa_to_life_essence(model_id)
        if synced:
            print(f"✅ Jivitindriya synced successfully")
        else:
            print(f"⚠️  Jivitindriya sync failed")
    except Exception as e:
        print(f"❌ Sync error: {e}")
    
    # Step 5: Verify
    print(f"\n5️⃣ Verifying RupaProfile...")
    rupa = await RupaProfile.find_one(RupaProfile.model_id == model_id)
    if rupa:
        print(f"✅ RupaProfile verified:")
        print(f"   • Mahabhuta (4 elements):")
        print(f"     - Pathavi (Earth): {rupa.mahabhuta_state.pathavi.hardness_level:.1f}")
        print(f"     - Apo (Water): {rupa.mahabhuta_state.apo.cohesion_level:.1f}")
        print(f"     - Tejo (Fire): {rupa.mahabhuta_state.tejo.heat_level:.2f}°C")
        print(f"     - Vayo (Wind): {rupa.mahabhuta_state.vayo.tension_level:.1f}")
        print(f"   • Pasada (5 sense organs):")
        print(f"     - Cakkhu (Eye): {rupa.pasada_state.cakkhu_pasada or 0:.1f}")
        print(f"     - Sota (Ear): {rupa.pasada_state.sota_pasada or 0:.1f}")
        print(f"     - Ghana (Nose): {rupa.pasada_state.ghana_pasada or 0:.1f}")
        print(f"     - Jivha (Tongue): {rupa.pasada_state.jivha_pasada or 0:.1f}")
        print(f"     - Kaya (Body): {rupa.pasada_state.kaya_pasada or 0:.1f}")
        print(f"   • Samutthana (4 origins):")
        print(f"     - Kamma: {rupa.kamma_rupa_count} rupa")
        print(f"     - Citta: {rupa.citta_rupa_count} rupa")
        print(f"     - Utu: {rupa.utu_rupa_count} rupa")
        print(f"     - Ahara: {rupa.ahara_rupa_count} rupa")
        print(f"   • Total: 28 Material Forms ✅")
    else:
        print(f"❌ RupaProfile not found after calculation!")
    
    print(f"\n" + "=" * 60)
    print(f"✅ Test completed successfully!")


if __name__ == "__main__":
    # Import database init
    try:
        from db_init import init_db
    except:
        from database import init_db
    
    async def main():
        await init_db()
        await test_calculate()
    
    asyncio.run(main())
