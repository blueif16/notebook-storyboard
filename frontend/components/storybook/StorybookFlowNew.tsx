'use client';

import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { LandingPage } from './LandingPage';
import { StyleConfigPage } from './StyleConfigPage';
import { BriefInputPage } from './BriefInputPage';
import { GenerationLoading } from './GenerationLoading';
import { CharacterApproval } from './CharacterApprovalNew';
import { StoryReader } from './StoryReader';
import { pageVariants } from '@/lib/animations';
import { storybookAPI, StorybookAPIError } from '@/lib/api/storybook';
import type { Character, Story, StoryPageUI } from '@/types/storybook';

type Page = 'landing' | 'style' | 'brief' | 'loading-characters' | 'approval' | 'loading-story' | 'reading' | 'error';

interface StoryData {
  style: string;
  brief: string;
  storyId: string | null;
  characters: Character[];
  story: Story | null;
}

export function StorybookFlow() {
  const [currentPage, setCurrentPage] = useState<Page>('landing');
  const [storyData, setStoryData] = useState<StoryData>({
    style: '',
    brief: '',
    storyId: null,
    characters: [],
    story: null,
  });
  const [error, setError] = useState<string | null>(null);

  const handleBegin = () => {
    setCurrentPage('style');
  };

  const handleStyleSelect = (style: string) => {
    setStoryData(prev => ({ ...prev, style }));
    setCurrentPage('brief');
  };

  const handleBriefSubmit = async (brief: string) => {
    setStoryData(prev => ({ ...prev, brief }));
    setCurrentPage('loading-characters');
    setError(null);

    try {
      // Phase 1: Generate characters
      const response = await storybookAPI.generateCharacters({
        story_text: brief,
        style: storyData.style,
      });

      setStoryData(prev => ({
        ...prev,
        storyId: response.story_id,
        characters: response.characters,
      }));
      setCurrentPage('approval');
    } catch (err) {
      console.error('Character generation failed:', err);
      setError(err instanceof StorybookAPIError ? err.message : 'Failed to generate characters');
      setCurrentPage('error');
    }
  };

  const handleCharacterContinue = async () => {
    if (!storyData.storyId) {
      setError('Story ID is missing');
      setCurrentPage('error');
      return;
    }

    setCurrentPage('loading-story');
    setError(null);

    try {
      // Phase 2: Generate story
      const response = await storybookAPI.generateStory({
        story_id: storyData.storyId,
        aspect_ratio: '16:9',
      });

      setStoryData(prev => ({
        ...prev,
        story: response.story,
      }));
      setCurrentPage('reading');
    } catch (err) {
      console.error('Story generation failed:', err);
      setError(err instanceof StorybookAPIError ? err.message : 'Failed to generate story');
      setCurrentPage('error');
    }
  };

  const handleBackToLanding = () => {
    setCurrentPage('landing');
    setStoryData({
      style: '',
      brief: '',
      storyId: null,
      characters: [],
      story: null,
    });
    setError(null);
  };

  const handleRetry = () => {
    setCurrentPage('brief');
    setError(null);
  };

  // Convert Story pages to UI format
  const storyPages: StoryPageUI[] = storyData.story?.pages.map(page => ({
    imageUrl: page.generated_image_url || '',
    text: page.plot,
  })) || [];

  return (
    <div className="storybook-flow min-h-screen">
      <AnimatePresence mode="wait">
        {/* Landing Page */}
        {currentPage === 'landing' && (
          <motion.div key="landing" variants={pageVariants} initial="initial" animate="enter" exit="exit">
            <LandingPage onBegin={handleBegin} />
          </motion.div>
        )}

        {/* Style Selection */}
        {currentPage === 'style' && (
          <motion.div key="style" variants={pageVariants} initial="initial" animate="enter" exit="exit">
            <StyleConfigPage onNext={handleStyleSelect} onBack={handleBackToLanding} />
          </motion.div>
        )}

        {/* Brief Input */}
        {currentPage === 'brief' && (
          <motion.div key="brief" variants={pageVariants} initial="initial" animate="enter" exit="exit">
            <BriefInputPage onNext={handleBriefSubmit} onBack={() => setCurrentPage('style')} />
          </motion.div>
        )}

        {/* Loading Characters */}
        {currentPage === 'loading-characters' && (
          <motion.div key="loading-characters" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <GenerationLoading />
          </motion.div>
        )}

        {/* Character Approval */}
        {currentPage === 'approval' && storyData.characters.length > 0 && (
          <motion.div key="approval" variants={pageVariants} initial="initial" animate="enter" exit="exit">
            <CharacterApproval characters={storyData.characters} onContinue={handleCharacterContinue} />
          </motion.div>
        )}

        {/* Loading Story */}
        {currentPage === 'loading-story' && (
          <motion.div key="loading-story" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <GenerationLoading />
          </motion.div>
        )}

        {/* Story Reader */}
        {currentPage === 'reading' && storyPages.length > 0 && (
          <motion.div key="reading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <StoryReader pages={storyPages} onHome={handleBackToLanding} />
          </motion.div>
        )}

        {/* Error Page */}
        {currentPage === 'error' && (
          <motion.div key="error" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <div className="error-page min-h-screen bg-[#F5F1E8] flex flex-col items-center justify-center px-6">
              <div className="error-card bg-white rounded-3xl shadow-xl p-8 max-w-md w-full border-4 border-[#C17C74]">
                <h2 className="text-3xl font-bold text-[#C17C74] mb-4 text-center" style={{ fontFamily: 'Comic Sans MS, cursive' }}>
                  Oops!
                </h2>
                <p className="text-[#8B7355] text-center mb-6">{error}</p>
                <div className="flex gap-4 justify-center">
                  <button
                    onClick={handleRetry}
                    className="px-6 py-3 rounded-full bg-[#6B8FA3] text-white border-2 border-[#8B7355]"
                  >
                    Try Again
                  </button>
                  <button
                    onClick={handleBackToLanding}
                    className="px-6 py-3 rounded-full bg-white text-[#8B7355] border-2 border-[#8B7355]"
                  >
                    Go Home
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
