import asyncio
import sys
from morphik import Morphik

async def test_morphik_colpali():
    """Тест интеграции Morphik + ColPali + Modal"""
    try:
        print("🚀 Testing Morphik + ColPali integration...")
        
        db = Morphik("http://localhost:8000", is_local=True)
        
        # 1. Тест обычных embeddings
        print("1️⃣ Testing regular embeddings...")
        doc1 = await db.ingest_text(
            content="Regular document without ColPali", 
            use_colpali=False,
            filename="regular.txt"
        )
        print(f"✅ Regular document: {doc1.external_id}")
        
        # 2. Тест ColPali embeddings
        print("2️⃣ Testing ColPali embeddings...")
        doc2 = await db.ingest_text(
            content="ColPali document for multimodal processing", 
            use_colpali=True,
            filename="colpali.txt"
        )
        print(f"✅ ColPali document: {doc2.external_id}")
        
        # 3. Тест поиска
        print("3️⃣ Testing search...")
        chunks = await db.retrieve_chunks("multimodal processing", use_colpali=True, k=2)
        print(f"✅ ColPali search: {len(chunks)} chunks found")
        
        # 4. Тест запроса
        print("4️⃣ Testing query...")
        response = await db.query("What is this about?", use_colpali=True, k=2)
        print(f"✅ Generated response: {len(response.completion)} chars")
        
        print("\n🎉 ALL TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_morphik_colpali())
    sys.exit(0 if success else 1)
