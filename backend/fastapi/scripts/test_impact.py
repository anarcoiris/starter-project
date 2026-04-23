import httpx
import asyncio
import random

BASE_URL = "http://localhost:8000/api/v1"

async def test_impact_tracking():
    async with httpx.AsyncClient() as client:
        # 1. Obtener el primer artículo disponible
        print("🔍 Obteniendo artículos...")
        resp = await client.get(f"{BASE_URL}/articles/")
        articles = resp.json()
        
        if not articles:
            print("❌ No hay artículos en la DB. Abortando.")
            return

        target = articles[0]
        article_id = target["articleId"]
        initial_views = target.get("views", 0)
        print(f"✅ Artículo seleccionado: {target['title'][:50]}... (ID: {article_id})")
        print(f"📊 Vistas iniciales: {initial_views}")

        # 2. Simular múltiples lecturas
        num_reads = 5
        print(f"🚀 Simulando {num_reads} eventos de lectura...")
        
        for i in range(num_reads):
            read_event = {
                "userId": f"user_test_{random.randint(100, 999)}",
                "readTimeSeconds": random.randint(10, 60)
            }
            resp = await client.post(f"{BASE_URL}/articles/{article_id}/read", json=read_event)
            if resp.status_code == 200:
                print(f"  [+] Lectura {i+1} registrada")
            else:
                print(f"  [!] Error en lectura {i+1}: {resp.text}")

        # 3. Verificar incremento
        print("🔄 Verificando actualización en DB...")
        resp = await client.get(f"{BASE_URL}/articles/")
        updated_articles = resp.json()
        updated_target = next(a for a in updated_articles if a["articleId"] == article_id)
        
        final_views = updated_target.get("views", 0)
        print(f"🏁 Vistas finales: {final_views}")
        
        if final_views == initial_views + num_reads:
            print("✨ TEST EXITOSO: El impacto se registró correctamente.")
        else:
            print(f"❌ TEST FALLIDO: Se esperaban {initial_views + num_reads} vistas.")

if __name__ == "__main__":
    asyncio.run(test_impact_tracking())
