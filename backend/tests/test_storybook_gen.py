"""故事书生成服务单元测试"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from app.services.storybook_gen import storybook_gen, _optimize_plot_for_image
from app.models import Character, Story, StoryPage


@pytest.fixture
def mock_instructor_client():
    """模拟 instructor 客户端"""
    client = Mock()
    client.chat.completions.create = Mock()
    return client


@pytest.fixture
def sample_characters():
    """示例角色数据"""
    return [
        Character(name="小明", description="一个勇敢的男孩", image_id="char_001"),
        Character(name="小红", description="聪明的女孩", image_id="char_002")
    ]


@pytest.fixture
def sample_story():
    """示例故事数据"""
    return Story(
        characters=[
            Character(name="小明", description="勇敢的男孩", image_id="char_001")
        ],
        pages=[
            StoryPage(
                page_number=1,
                plot="小明在森林里探险",
                character_names=["小明"],
                reference_page_numbers=[],
                generated_image_id="img_001"
            )
        ]
    )


class TestStorybookGen:
    """故事书生成主流程测试"""

    @pytest.mark.asyncio
    async def test_storybook_gen_basic_flow(self, mock_instructor_client, sample_characters):
        """测试基本生成流程"""
        with patch('app.services.storybook_gen.instructor.from_provider') as mock_provider, \
             patch('app.services.storybook_gen.google_text_to_image') as mock_text_img, \
             patch('app.services.storybook_gen.google_image_to_image') as mock_img_img, \
             patch('app.services.storybook_gen._optimize_plot_for_image') as mock_optimize:

            # 配置 mock
            mock_provider.return_value = mock_instructor_client
            mock_text_img.return_value = "img_001"
            mock_img_img.return_value = "img_002"
            mock_optimize.return_value = "优化后的场景描述"

            # 模拟 LLM 返回
            enhanced_story = Mock(story="扩充后的故事内容")
            character_list = Mock(characters=sample_characters)
            story_result = Story(
                characters=[],
                pages=[
                    StoryPage(
                        page_number=1,
                        plot="第一页情节",
                        character_names=["小明"],
                        reference_page_numbers=[]
                    )
                ]
            )

            mock_instructor_client.chat.completions.create.side_effect = [
                enhanced_story,
                character_list,
                story_result
            ]

            # 执行测试
            result = await storybook_gen("测试故事", "16:9")

            # 验证结果
            assert isinstance(result, Story)
            assert len(result.characters) == 2
            assert len(result.pages) == 1
            assert result.pages[0].generated_image_id is not None

    @pytest.mark.asyncio
    async def test_storybook_gen_with_reference_pages(self, mock_instructor_client, sample_characters):
        """测试带参考页面的生成"""
        with patch('app.services.storybook_gen.instructor.from_provider') as mock_provider, \
             patch('app.services.storybook_gen.google_text_to_image') as mock_text_img, \
             patch('app.services.storybook_gen.google_image_to_image') as mock_img_img, \
             patch('app.services.storybook_gen._optimize_plot_for_image') as mock_optimize:

            mock_provider.return_value = mock_instructor_client
            mock_text_img.return_value = "img_001"
            mock_img_img.return_value = "img_002"
            mock_optimize.return_value = "优化场景"

            enhanced_story = Mock(story="故事")
            character_list = Mock(characters=sample_characters)
            story_result = Story(
                characters=[],
                pages=[
                    StoryPage(page_number=1, plot="第一页", character_names=["小明"], reference_page_numbers=[]),
                    StoryPage(page_number=2, plot="第二页", character_names=["小红"], reference_page_numbers=[1])
                ]
            )

            mock_instructor_client.chat.completions.create.side_effect = [
                enhanced_story, character_list, story_result
            ]

            result = await storybook_gen("测试", "16:9")

            assert len(result.pages) == 2
            assert result.pages[1].reference_page_numbers == [1]
            assert mock_img_img.called


class TestOptimizePlot:
    """测试情节优化功能"""

    @pytest.mark.asyncio
    async def test_optimize_plot_basic(self):
        """测试基本情节优化"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="优化后的场景描述"))]
        mock_client.chat.completions.create.return_value = mock_response

        result = await _optimize_plot_for_image(
            mock_client,
            "小明在森林里探险",
            ["小明"]
        )

        assert result == "优化后的场景描述"
        assert mock_client.chat.completions.create.called
