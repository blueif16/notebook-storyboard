"""Unboxing Video工具 - 开箱视频分段生成"""
import os, re, shutil, asyncio, logging
from langchain_core.tools import tool
import instructor
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 从新的 service 模块导入函数
from .storage_service import (
    ensure_folder_structure,
    save_caption_to_batch,
    save_to_supabase,
    get_image_url_from_asset_id,
    get_local_file_path_from_asset_id,
    update_task_status,
    current_user_id
)
from .image_service import (
    fal_subscribe,
    unified_image_gen_service,
    unified_image_to_image_gen_service
)
from .video_service import (
    video_gen_service,
    stitch_videos,
    stitch_campaign_videos,
    first_end_to_video
)

load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 视频分段模型
class Segment(BaseModel):
    """视频片段分段信息 - 用于分析和生成分段视频"""
    id: int = Field(..., description="分段ID，自增")
    plot: str = Field(..., description="该分段的情节描述")
    first_frame: Optional[str] = Field(None, description="起始帧图片asset_id")
    end_frame: Optional[str] = Field(None, description="结束帧图片asset_id")

script_writer_prompt = """Role and Context
You are a professional unboxing video director with 10+ years of experience in product cinematography and e-commerce content creation. Your specialty is crafting engaging product reveal sequences that maximize viewer engagement and highlight product features effectively.

Task Instructions
Transform product asset data into three-part unboxing video scripts. Each part must be exactly 4 seconds (20-30 words). Analyze all provided asset descriptions to automatically detect if back/rear views exist—if mentioned, use 360 degree rotation in Part 3; if not mentioned, use tactile exploration.
Include brief product descriptions naturally in the script based on the product category, purpose, materials, and key features. Reference all relevant asset IDs (box, product, accessories) naturally throughout.

Output Format
Generate three sequential script parts:

PART 1 - BOX PRESENTATION (4 seconds)
- Position box asset on table center
- Slowly remove lid/cover
- Include brief mention of product type/category
- Reference box ID if provided

PART 2 - PRODUCT EXTRACTION (4 seconds)
- Use one hand to lift product from packaging
- Place product at table center
- Move box aside, but still keep it in the frame, and its shape and appearance should be the same
- Reference main product ID

PART 3 - PRODUCT SHOWCASE (4 seconds)
- Only if the back view of product is provided in the assets list, rotate product 360 degrees clockwise, end with back view visible, describe back features
- IF no back view mentioned: Touch and explore surfaces, demonstrate texture, build quality, functional elements
- Reference product ID

Writing Style Requirements:
- Present tense, active voice only
- Use pacing descriptors: slowly, gently, deliberately, smoothly
- Each sentence describes visible action or movement, but do not add unnecessary details that you don't know about, only info you can trust is from the provided asset descriptions
- Asset IDs appear naturally in context with brief description in parentheses on first mention
- At each plot, also include some description of current setting, what's in the frame and how they are placed
- Better have the hand wearing gloves everytime and keep it the same, better use only one hand during the full process, also be more specific about the hand's movement and action, from which direction, at the end state of each plot, I don't want hand to be included

Example Output:
Input assets:
- 6525c1c8-5adc-4d34-94d6-feb3797ed601: premium red gift box
- e8df9364-a5c4-4e55-acc4-7aeab3ef0409: white leather luxury bag, front view studio shot

Output:
PART 1 - BOX PRESENTATION
The bx089 (premium black gift box) sits centered on the table, very important to mention the lid is completely closed. Hands gently lift the lid, gradully opening it and revealing ed112 (white leather crossbody bag) beneath. Then withdraw the hand and keep the lid completely open and the bag fully visible.

PART 2 - PRODUCT EXTRACTION
Using one hand, lift ed112 by its strap from bx089. Place ed112 at the table center, move bx089 aside with the lid beside the box but keep it in the frame.

PART 3 - In detail showcase of the product
Slowly touches the bag and show the details. Slowly move the hand around the bag. Here keep the box and lidin the last frame totally unchanged.
"""

def get_instructor_client():
    """延迟初始化instructor客户端"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return instructor.from_provider("openai/gpt-5", api_key=api_key)

def get_openai_client():
    """延迟初始化OpenAI客户端"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return AsyncOpenAI(api_key=api_key)

class VideoSegments(BaseModel):
    """视频分段集合 - 包含多个Segment"""
    segments: List[Segment] = Field(..., description="视频分段列表")

class FrameImageGeneration(BaseModel):
    """帧图片生成模型"""
    prompt: str = Field(..., description="Prompt for the current frame's generation")
    image_asset_id: List[str] = Field(..., description="ref image asset ids, only those needed for the generation of the current frame and is not existing in previous frame")

async def extract_video_segments(prompt: str) -> List[Segment]:
    """使用instructor从prompt中提取结构化的视频分段信息"""
    try:
        client=get_instructor_client()
        if not client:
            print(f"❌ [UNBOXING_VIDEO_TOOL] OPENAI_API_KEY未配置")
            return []

        print(f"🔍 [UNBOXING_VIDEO_TOOL] 开始提取视频分段信息...")

        response = client.chat.completions.create(
            response_model=VideoSegments,
            messages=[
                {
                    "role": "system",
                    "content": script_writer_prompt
                },
                {
                    "role": "user",
                    "content": f"Analyze this video description and break it into segments:\n\n{prompt}"
                }
            ]
        )

        print(f"✅ [UNBOXING_VIDEO_TOOL] 成功提取 {len(response.segments)} 个分段")
        for seg in response.segments:
            print(f"   📹 分段{seg.id}: {seg.plot[:50]}...")

        return response.segments

    except Exception as e:
        print(f"❌ [UNBOXING_VIDEO_TOOL] 提取分段失败: {e}")
        return []

async def extract_start_frame(plot: str) -> FrameImageGeneration:
    """从情节描述中提取起始帧生成信息"""
    client=get_instructor_client()
    if not client:
        raise RuntimeError("OPENAI_API_KEY未配置")
    response = client.chat.completions.create(
        response_model=FrameImageGeneration,
        messages=[
            {
                "role": "system",
                "content": """
                    You are an expert prompt generator for initial scene generation.

                    **TASK:** Create an image generation prompt for the FIRST FRAME from a plot description.

                    **ANALYSIS:**
                    - Identify which assets are VISIBLE in the starting state
                    - Understand hidden vs. visible (if a bag is inside a closed box, only include the box)
                    - Extract asset IDs only for objects appearing in frame 1

                    **PROMPT FORMULA:** Subject + State/Position + Spatial Relationships

                    Example structure:
                    - "A closed white box sits on a wooden table"
                    - "A white bag and wooden crate sit side by side on a table, bag on the left"
                    - "An open white box on a table with a blue bag visible inside"

                    **RULES:**
                    - NEVER mention asset IDs in prompt text (use descriptive names)
                    - ONLY include VISIBLE assets in starting state
                    - If object is hidden (inside closed container), exclude it
                    - NO elements not in plot/asset list
                    - Keep environment minimal (simple table, neutral background)
                    - NO lighting, camera angles, or artistic descriptions
                    - Focus on positions and states only

                    **OUTPUT FORMAT:**
                    ```
                    Prompt: [Complete generation instruction]
                    Asset IDs to Include: [Only VISIBLE assets in frame 1]
                    ```

                    **EXAMPLES:**

                    Plot: "A closed white box sits on a table. Inside is a blue bag (hidden)."
                    ```
                    Prompt: A closed white box sits in the center of a wooden table.
                    Asset IDs: [white_box_id]
                    ```

                    Plot: "An open white box on a table with a blue bag visible inside."
                    ```
                    Prompt: An open white box sits on a wooden table with a blue bag visible inside the box.
                    Asset IDs: [white_box_id, blue_bag_id]
                    ```
                    """
            },
            {
                "role": "user",
                "content": f"Plot: {plot}"
            }
        ]
    )
    return response

async def extract_video_prompt(plot: str, previous_segment_prompt: str = None) -> str:
    """从情节描述中生成视频生成prompt"""
    openai_client=get_openai_client()
    if not openai_client:
        raise RuntimeError("OPENAI_API_KEY未配置")
    response = await openai_client.chat.completions.create(
        model="gpt-5",
        messages=[
            {
                "role": "system",
                "content": """You are the best first-end frame video prompt generator.
Your task: Given a plot description, two frame states (start/end), and optionally the previous segment's video prompt, generate a concise video prompt that describes the transition motion with precise directional details and maintains visual consistency.
Rules:

Be concise but directionally specific (3-4 sentences max)
Include precise movement directions: from right/left, upward/downward, toward/away from camera, clockwise/counterclockwise
Maintain consistency: If previous prompt mentions features of hands, body, color of gloves, movement directions, keep them identical for operation consistency
Describe the action path clearly: where objects/hands enter, move, and exit
Add camera movement only if needed (push in, pull back, slight tilt, pan)
Include studio-quality ASMR sound matching the action (box opening, bag rustling, gentle touches)
Use present tense, active voice
Skip IDs - describe objects naturally (e.g., "luxury watch box" not "6525c1c8...")

```

**Example:**
```
Previous segment: "Right hand in black glove enters from right side of frame, reaches toward silver box on gray table"

Current plot: "The luxury watch box is centered on a matte gray table, lid fully closed. A right hand in black gloves slowly lifts and removes the lid upward to reveal the watch inside, then exits frame to the right, leaving the box open."

Output: "Right hand in black glove grips box lid enters from right side of frame, lifts it upward and removes it completely, revealing watch inside. Hand exits right side of frame with lid, leaving open box centered on table.\""""
            },
            {
                "role": "user",
                "content": f"Convert this plot into a video generation prompt:\n\n{plot}, you can refer to some details for consistency from previous segment's prompt: {previous_segment_prompt}"
            }
        ]
    )
    return response.choices[0].message.content
async def extract_end_frame(plot: str, previous_frame_prompt: str) -> FrameImageGeneration:
    """从情节描述中提取结束帧生成信息"""
    client=get_instructor_client()
    if not client:
        raise RuntimeError("OPENAI_API_KEY未配置")
    response = client.chat.completions.create(
        response_model=FrameImageGeneration,
        messages=[
            {
                "role": "system",
                "content": """
You are an expert prompt generator for sequential image editing.

**CRITICAL: Describe FINAL STATES, not actions or motion.**

❌ WRONG: "A hand lifts the bag from the box"
✅ RIGHT: "The bag sits on the table. The box is empty."

**ANALYSIS:**
- Ignore motion/process in plot (hand movements, lifting, sliding)
- Identify FINAL STATE: Where are objects? What's visible? 
- Extract asset IDs for newly visible objects
- **EDGE CASE**: If an asset was hidden/blocked in previous frame (inside closed box, behind object, etc.) and now becomes fully visible, extract its asset ID even if it appeared earlier

**PROMPT FORMULA:**

1. **Reference images**: State what images are provided
   - Always: "Using the provided previous frame image as the basis"
   - If new/newly-visible assets: "and the provided [asset name] image"

2. **Final state**: Describe what IS visible (present tense)
   - "The box lid is open, revealing the white bag inside"
   - "The bag sits centered on the table"
   - "No hands are visible"
   - "If bag is picked up from the box, the box should be empty"

3. **Consistency preservation**: Be SPECIFIC about unchanged elements
   - List concrete elements: "Keep the wooden box, camera angle, lighting, background texture, and table surface exactly as shown in the reference image."
   - NOT vague phrases like "Keep everything else the same"

**RULES:**
- NEVER describe actions/motion (lifting, sliding, entering)
- ALWAYS mention provided asset images in the prompt
- Extract asset ID if previously hidden (inside box, blocked) and now visible
- NEVER mention asset IDs in prompt (use descriptive names)
- Describe final positions only
- Be SPECIFIC about what stays unchanged (box position, lighting, camera angle, background, etc.)

**OUTPUT:**
```
Prompt: [Complete instruction]
Asset IDs: [Only NEW or newly-visible objects]
```

**EXAMPLES:**

Plot: "A hand lifts the box lid, revealing a blue bag. The hand withdraws."

CORRECT:
```
Prompt: Using the provided previous frame image as the basis and the provided blue bag image, the box lid is fully open with the blue bag visible inside. No hands are visible. Keep the box position, camera angle, lighting, background, and table surface exactly as shown in the reference image.
Asset IDs: [blue_bag_id]
```
(Bag was hidden, now visible - extract ID)

---

Plot: "A hand lifts the white bag from box to table center. Hand slides box left and exits."

CORRECT:
```
Prompt: Using the provided previous frame image as the basis and the provided white bag image, the white bag sits centered on the table. The open empty box is positioned on the left side of the table. No hands are visible. Keep the camera angle, lighting, background texture, and table surface exactly as shown in the reference image.
Asset IDs: [white_bag_id]
```
(Bag was inside box, now fully visible on table - extract ID)

---

Plot: "A hand traces the bag surface. Hand withdraws."

CORRECT:
```
Prompt: Using the provided previous frame image as the basis, the white bag remains centered on the table in its current position. No hands are visible. Keep the box position, camera angle, lighting, background, and table surface exactly as shown in the reference image.
Asset IDs: []
```
(Bag was already fully visible and hasn't moved - no ID needed)

**KEY: If asset was hidden/blocked and becomes visible, extract its ID and mention the image is provided. Always list specific elements to preserve rather than using vague "keep everything else the same" language.**
"""
            },
            {
                "role": "user",
                "content": f"Plot: {plot} \n Previous frame's prompt: {previous_frame_prompt}"
            }
        ]
    )
    return response

async def generate_segment_end_frames(segments: List[Segment], campaign_id: str, batch_id: str) -> tuple[List[Segment], dict]: # 为每个分段生成结束帧图片
    """为每个分段生成结束帧，并将asset_id连接到下一个分段的起始帧
    
    Returns:
        tuple: (segments, prompts_info) - segments列表和prompts信息字典
    """
    print(f"\n{'='*80}")
    print(f"🎨 [GENERATE_END_FRAMES] 开始生成分段结束帧")
    print(f"📋 共 {len(segments)} 个分段")
    print(f"{'='*80}\n")
    
    previous_frame_prompt = "" # 初始化previous_frame_prompt，用于后续结束帧生成
    prompts_info = {} # 存储所有提取的prompts信息
    
    # 首先为第一个分段生成第一帧（起始帧）
    if segments and len(segments) > 0:
        first_segment = segments[0]
        print(f"\n--- 为第一个分段生成第一帧（起始状态） ---")
        
        try:
            # 提取起始帧FrameImageGeneration
            first_frame = await extract_start_frame(first_segment.plot)
            print(f"📝 [分段{first_segment.id}] 提取起始帧prompt: {first_frame.prompt[:80]}...")
            print(f"📝 [分段{first_segment.id}] 提取asset_ids: {first_frame.image_asset_id}")
            
            # 保存起始帧prompt信息
            prompts_info[f"segment_{first_segment.id}_start"] = {
                "type": "start_frame",
                "prompt": first_frame.prompt,
                "asset_ids": first_frame.image_asset_id
            }

            # 使用所有提取到的asset_ids，return_id=True直接返回asset_id
            first_frame_asset_id = await unified_image_to_image_gen_service(
                prompt=first_frame.prompt,
                image_asset_id=first_frame.image_asset_id,
                aspect_ratio="16:9",
                return_id=True
            )
            print(f"✅ [分段{first_segment.id}] 第一帧生成完成")
            
            if first_frame_asset_id:
                first_segment.first_frame = first_frame_asset_id
                previous_frame_prompt = first_frame.prompt # 更新previous_frame_prompt为起始帧的prompt
                print(f"💾 [分段{first_segment.id}] 第一帧asset_id: {first_frame_asset_id}")
            else:
                print(f"⚠️  [分段{first_segment.id}] 生成第一帧失败")
        except Exception as e:
            print(f"❌ [分段{first_segment.id}] 生成第一帧异常: {e}")
    
    for i, segment in enumerate(segments):
        print(f"\n--- 处理分段 {segment.id} ({i+1}/{len(segments)}) ---")
        
        # 确定当前分段的起始帧asset_id
        if i == 0:
            current_first_frame_id = segment.first_frame # 第一个分段使用刚生成的第一帧
        else:
            current_first_frame_id = segments[i-1].end_frame # 使用上一个分段的结束帧
            segment.first_frame = current_first_frame_id
        
        print(f"📸 [分段{segment.id}] 起始帧ID: {current_first_frame_id}")
        
        # 提取结束帧生成信息，包含previous frame prompt
        try:
            frame_gen = await extract_end_frame(segment.plot, previous_frame_prompt)
            print(f"📝 [分段{segment.id}] 提取结束帧prompt: {frame_gen.prompt[:80]}...")
            print(f"📝 [分段{segment.id}] 提取asset_ids: {frame_gen.image_asset_id}")
            
            # 保存结束帧prompt信息
            prompts_info[f"segment_{segment.id}_end"] = {
                "type": "end_frame",
                "prompt": frame_gen.prompt,
                "asset_ids": frame_gen.image_asset_id
            }

            # 使用所有提取到的asset_ids（不只是第一个），return_id=True直接返回asset_id
            end_frame_asset_id = await unified_image_to_image_gen_service(
                prompt=frame_gen.prompt,
                image_asset_id=frame_gen.image_asset_id + [segment.first_frame],
                aspect_ratio="16:9",
                return_id=True
            )
            print(f"✅ [分段{segment.id}] 结束帧生成完成")
            
            if end_frame_asset_id:
                segment.end_frame = end_frame_asset_id # 存储到end_frame字段
                previous_frame_prompt = frame_gen.prompt # 更新previous_frame_prompt为当前生成的prompt
                print(f"💾 [分段{segment.id}] 结束帧asset_id: {end_frame_asset_id}")
                
                # 如果有下一个分段，设置它的first_frame字段
                if i < len(segments) - 1:
                    segments[i+1].first_frame = end_frame_asset_id
                    print(f"🔗 [分段{segment.id}] 链接到下一个分段的起始帧")
            else:
                print(f"⚠️  [分段{segment.id}] 生成失败")
                
        except Exception as e:
            print(f"❌ [分段{segment.id}] 生成结束帧失败: {e}")
            continue
    
    print(f"\n{'='*80}")
    print(f"✅ [GENERATE_END_FRAMES] 所有分段处理完成")
    print(f"{'='*80}\n")
    
    return segments, prompts_info

def copy_final_frames_to_directory(campaign_id: str, batch_id: str, segments: List[Segment]) -> str: # 复制最终帧到专用目录
    """将第一个分段的第一帧和所有分段的结束帧复制到final_frames目录（不重复）"""
    print(f"\n{'='*80}")
    print(f"📁 [COPY_FINAL_FRAMES] 开始整理最终帧")
    print(f"{'='*80}\n")
    
    # 创建final_frames目录
    base_dir = Path(__file__).parent.parent.parent / "generated_campaigns"
    final_frames_dir = base_dir / campaign_id / batch_id / "final_frames"
    final_frames_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 [COPY_FINAL_FRAMES] 目标目录: {final_frames_dir}")
    
    # 收集需要复制的asset_id（不重复）
    frames_to_copy = []
    copied_asset_ids = set() # 用于去重
    
    # 第一个分段的第一帧
    if segments and len(segments) > 0 and segments[0].first_frame:
        first_frame_id = segments[0].first_frame
        if first_frame_id not in copied_asset_ids:
            frames_to_copy.append(("first_frame_segment_1", first_frame_id))
            copied_asset_ids.add(first_frame_id)
            print(f"📸 [COPY_FINAL_FRAMES] 添加第一帧: {first_frame_id}")
    
    # 所有分段的结束帧
    for segment in segments:
        if segment.end_frame and segment.end_frame not in copied_asset_ids:
            frames_to_copy.append((f"end_frame_segment_{segment.id}", segment.end_frame))
            copied_asset_ids.add(segment.end_frame)
            print(f"📸 [COPY_FINAL_FRAMES] 添加分段{segment.id}结束帧: {segment.end_frame}")
    
    print(f"📊 [COPY_FINAL_FRAMES] 共需要复制 {len(frames_to_copy)} 个不重复的帧")
    
    # 复制每一帧
    copied_files = []
    for frame_name, asset_id in frames_to_copy:
        try:
            print(f"\n--- 处理 {frame_name} (asset_id: {asset_id}) ---")
            
            # 获取本地文件路径
            source_path = get_local_file_path_from_asset_id(asset_id)
            if not source_path:
                print(f"⚠️  [COPY_FINAL_FRAMES] 无法获取本地文件路径，跳过")
                continue
            
            # 复制文件
            dest_filename = f"{frame_name}.jpg"
            dest_path = final_frames_dir / dest_filename
            shutil.copy2(source_path, dest_path) # copy2保留元数据
            
            print(f"✅ [COPY_FINAL_FRAMES] 已复制: {source_path} -> {dest_path}")
            copied_files.append(str(dest_path))
            
        except Exception as e:
            print(f"❌ [COPY_FINAL_FRAMES] 处理{frame_name}时出错: {e}")
            continue
    
    print(f"\n{'='*80}")
    print(f"✅ [COPY_FINAL_FRAMES] 完成! 共复制 {len(copied_files)} 个帧")
    print(f"📁 [COPY_FINAL_FRAMES] 保存目录: {final_frames_dir}")
    print(f"{'='*80}\n")
    
    return str(final_frames_dir)

@tool
async def general_video_gen(campaign_id: str, batch_id: str, prompt: str) -> str: # 生成通用视频
    """Generate unboxing video content by extracting segments from prompt and creating video.
    
    Args:
        campaign_id: Campaign UUID identifier
        batch_id: Batch identifier (usually a number like "1")
        prompt: Video description/script that will be analyzed into segments
        
    Returns:
        Success message with extracted segments and generation details
    """
    print(f"\n{'='*80}")
    print(f"🎬 [UNBOXING_VIDEO_TOOL] 工具调用开始")
    print(f"📋 Campaign ID: {campaign_id}")
    print(f"📋 Batch ID: {batch_id}")
    print(f"📋 原始Prompt: {prompt}")
    print(f"{'='*80}\n")
    
    try:
        # 使用instructor提取视频分段
        segments = await extract_video_segments(prompt)
        
        if not segments:
            return "Error: Failed to extract video segments from prompt"
        
        # 为每个分段生成结束帧图片（所有asset_ids从segments中提取）
        segments, prompts_info = await generate_segment_end_frames(segments, campaign_id, batch_id)
        
        # 复制最终帧到专用目录（重用image_service已保存的文件）
        final_frames_dir = copy_final_frames_to_directory(campaign_id, batch_id, segments)
        
        # 为每个分段生成视频
        print(f"\n{'='*80}")
        print(f"🎬 [UNBOXING_VIDEO_TOOL] 开始生成分段视频")
        print(f"{'='*80}\n")
        
        video_paths = []
        previous_video_prompt = None # 初始化前一个分段的video prompt
        for i, segment in enumerate(segments):
            if not segment.first_frame or not segment.end_frame:
                print(f"⚠️  [分段{segment.id}] 缺少帧资产，跳过视频生成")
                continue
            
            try:
                print(f"\n--- 生成分段{segment.id}视频 ---")
                # 生成视频prompt，除第一个segment外都传入前一个segment的video prompt
                if i == 0:
                    video_prompt = await extract_video_prompt(segment.plot)
                    print(f"📝 [分段{segment.id}] 视频prompt (首个分段): {video_prompt}")
                else:
                    video_prompt = await extract_video_prompt(segment.plot, previous_video_prompt)
                    print(f"📝 [分段{segment.id}] 视频prompt (参考前一分段): {video_prompt}")
                    print(f"   参考的前一分段prompt: {previous_video_prompt}")
                
                # 生成视频
                video_path = await first_end_to_video(
                    campaign_id=campaign_id,
                    batch_id=batch_id,
                    prompt=video_prompt,
                    first_frame_asset_id=segment.first_frame,
                    last_frame_asset_id=segment.end_frame,
                    model="wan", # 使用Wan-2.1模型（默认）
                    num_frames=81, # 默认最小帧数
                    frames_per_second=16, # 默认16fps，约5秒视频
                    aspect_ratio="16:9",
                    resolution="720p",
                    num_inference_steps=30, # 默认推理步数
                    return_id=False,
                    return_path=True  # 只返回本地文件路径用于拼接
                )
                video_paths.append(video_path)
                previous_video_prompt = video_prompt # 更新前一个video prompt
                print(f"✅ [分段{segment.id}] 视频生成完成: {video_path}")
                
            except Exception as e:
                print(f"❌ [分段{segment.id}] 视频生成失败: {e}")
                continue
        
        # 拼接所有视频
        stitched_video_path = ""
        if len(video_paths) > 0:
            print(f"\n{'='*80}")
            print(f"🎞️ [UNBOXING_VIDEO_TOOL] 开始拼接视频")
            print(f"📋 共{len(video_paths)}个视频片段")
            print(f"{'='*80}\n")
            
            try:
                stitched_video_path = await stitch_campaign_videos(
                    campaign_id=campaign_id,
                    batch_id=batch_id,
                    segment_paths=video_paths,
                    output_filename="final_stitched.mp4"
                )
                print(f"✅ [UNBOXING_VIDEO_TOOL] 视频拼接完成: {stitched_video_path}")
            except Exception as e:
                print(f"❌ [UNBOXING_VIDEO_TOOL] 视频拼接失败: {e}")
        
        # 构建结果信息
        result_lines = [
            f"✅ Successfully extracted and generated {len(segments)} video segments:",
            ""
        ]
        
        for segment in segments:
            result_lines.extend([
                f"Segment {segment.id}:",
                f"  Plot: {segment.plot}",
                f"  First Frame Asset ID: {segment.first_frame or 'N/A'}",
                f"  End Frame Asset ID: {segment.end_frame or 'N/A'}",
                ""
            ])
        
        result_lines.append(f"Campaign: {campaign_id}, Batch: {batch_id}")
        result_lines.append(f"")
        result_lines.append(f"🎞️ Final frames saved to: {final_frames_dir}")
        result_lines.append(f"   - first_frame_segment_1.jpg (first frame of segment 1)")
        result_lines.append(f"   - end_frame_segment_X.jpg (end frames of all segments)")
        result_lines.append(f"")
        
        if video_paths:
            result_lines.append(f"🎬 Generated {len(video_paths)} video segments")
            for i, path in enumerate(video_paths, 1):
                result_lines.append(f"   - Segment {i}: {path}")
            result_lines.append(f"")
        
        if stitched_video_path:
            result_lines.append(f"🎉 Final stitched video: {stitched_video_path}")
            result_lines.append(f"")
        
        result_lines.append(f"{'='*80}")
        result_lines.append(f"📝 LLM提取的图片生成Prompts:")
        result_lines.append(f"{'='*80}")
        
        for key, info in prompts_info.items():
            result_lines.append(f"")
            result_lines.append(f"🔹 {key} ({info['type']}):")
            result_lines.append(f"   Prompt: {info['prompt']}")
            result_lines.append(f"   Asset IDs: {info['asset_ids']}")
        
        result_msg = "\n".join(result_lines)
        
        print(f"🎉 [UNBOXING_VIDEO_TOOL] 视频分段生成完成!")
        print(f"{'='*80}\n")
        
        return result_msg
        
    except Exception as e:
        error_msg = f"General video generation failed: {e}"
        print(f"❌ [UNBOXING_VIDEO_TOOL] 错误: {error_msg}")
        return error_msg

