"""Test Agent-Based Storybook System"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.graphs import run_storybook_generation, compile_storybook_graph, create_initial_state
from app.tools import enhance_and_extract


async def test_graph_compilation():
    print("\n" + "="*60)
    print("TEST 1: Graph Compilation")
    print("="*60)
    try:
        graph = compile_storybook_graph()
        print("✅ Graph compiled")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_state_creation():
    print("\n" + "="*60)
    print("TEST 2: State Creation")
    print("="*60)
    try:
        state = create_initial_state("Test story")
        assert "messages" in state
        assert state["stage"] == "idle"
        print("✅ State created")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_single_tool():
    print("\n" + "="*60)
    print("TEST 3: enhance_and_extract Tool")
    print("="*60)
    try:
        result = await enhance_and_extract.ainvoke({
            "story_text": "Luna is a brave mouse who finds a magic book."
        })
        assert "enhanced_story" in result
        assert "characters" in result
        print(f"✅ Tool works - found {len(result['characters'])} characters")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_pipeline():
    print("\n" + "="*60)
    print("TEST 4: Full Pipeline (WILL COST API CREDITS)")
    print("="*60)
    print("⚠️  This generates real images!")
    
    try:
        result = await run_storybook_generation(
            user_input="Luna is a brave mouse who finds a glowing book with a treasure map.",
            thread_id="test-full"
        )
        
        print(f"\n✅ Pipeline complete!")
        print(f"   Storybook ID: {result.get('storybook_id')}")
        print(f"   Characters: {len(result.get('characters', []))}")
        print(f"   Pages: {len(result.get('pages', []))}")
        return True
    
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_tests(full: bool = False):
    print("\n" + "🧪 "*30)
    print("STORYBOOK AGENT TEST SUITE")
    print("🧪 "*30)
    
    results = []
    results.append(("Graph Compilation", await test_graph_compilation()))
    results.append(("State Creation", await test_state_creation()))
    results.append(("Tool Test", await test_single_tool()))
    
    if full:
        results.append(("Full Pipeline", await test_full_pipeline()))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, passed in results:
        print(f"{'✅' if passed else '❌'} {name}")
    
    passed = sum(1 for _, p in results if p)
    print(f"\n{passed}/{len(results)} tests passed")
    
    return passed == len(results)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="Run full pipeline (costs credits)")
    args = parser.parse_args()
    
    success = asyncio.run(run_tests(full=args.full))
    sys.exit(0 if success else 1)
