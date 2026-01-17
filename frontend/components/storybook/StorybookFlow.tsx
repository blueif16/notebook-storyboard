'use client';

import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { LandingPage } from './LandingPage';
import { StyleConfigPage } from './StyleConfigPage';
import { BriefInputPage } from './BriefInputPage';
import { GenerationLoading } from './GenerationLoading';
import { CharacterApproval } from './CharacterApproval';
import { StoryReader } from './StoryReader';
import { pageVariants } from '@/lib/animations';

type Page = 'landing' | 'style' | 'brief' | 'loading' | 'approval' | 'reading';

interface StoryData {
  style: string;
  brief: string;
  character: {
    imageUrl: string;
    name: string;
  } | null;
  pages: Array<{
    imageUrl: string;
    text: string;
  }>;
}

export function StorybookFlow() {
  const [currentPage, setCurrentPage] = useState<Page>('landing');
  const [storyData, setStoryData] = useState<StoryData>({
    style: '',
    brief: '',
    character: null,
    pages: []
  });

  const handleBegin = () => {
    setCurrentPage('style');
  };

  const handleStyleSelect = (style: string) => {
    setStoryData(prev => ({ ...prev, style }));
    setCurrentPage('brief');
  };

  const handleBriefSubmit = async (brief: string) => {
    setStoryData(prev => ({ ...prev, brief }));
    setCurrentPage('loading');

    // Simulate API call for character generation
    setTimeout(() => {
      setStoryData(prev => ({
        ...prev,
        character: {
          imageUrl: '/hero2.jpeg', // Use your actual generated character
          name: 'Story Character'
        }
      }));
      setCurrentPage('approval');
    }, 3000);
  };

  const handleCharacterApprove = async () => {
    setCurrentPage('loading');

    // Simulate API call for story generation
    setTimeout(() => {
      setStoryData(prev => ({
        ...prev,
        pages: [
          {
            imageUrl: '/hero1.jpeg',
            text: 'Once upon a time, in a magical land filled with wonder and dreams, there lived a curious little character who loved to explore.'
          },
          {
            imageUrl: '/hero2.jpeg',
            text: 'Every day brought new adventures and exciting discoveries. The world was full of mysteries waiting to be uncovered.'
          },
          {
            imageUrl: '/hero1.jpeg',
            text: 'Through forests deep and mountains high, our brave friend journeyed on, making friends and learning valuable lessons along the way.'
          },
          {
            imageUrl: '/hero2.jpeg',
            text: 'And so, with a heart full of joy and memories to cherish, our hero returned home, ready for the next great adventure.'
          }
        ]
      }));
      setCurrentPage('reading');
    }, 3000);
  };

  const handleCharacterRegenerate = () => {
    setCurrentPage('loading');
    setTimeout(() => {
      setStoryData(prev => ({
        ...prev,
        character: {
          imageUrl: '/hero1.jpeg',
          name: 'New Character'
        }
      }));
      setCurrentPage('approval');
    }, 2000);
  };

  const handleBackToLanding = () => {
    setCurrentPage('landing');
    setStoryData({
      style: '',
      brief: '',
      character: null,
      pages: []
    });
  };

  return (
    <div className="storybook-flow min-h-screen">
      <AnimatePresence mode="wait">
        {currentPage === 'landing' && (
          <motion.div
            key="landing"
            variants={pageVariants}
            initial="initial"
            animate="enter"
            exit="exit"
          >
            <LandingPage onBegin={handleBegin} />
          </motion.div>
        )}

        {currentPage === 'style' && (
          <motion.div
            key="style"
            variants={pageVariants}
            initial="initial"
            animate="enter"
            exit="exit"
          >
            <StyleConfigPage
              onNext={handleStyleSelect}
              onBack={handleBackToLanding}
            />
          </motion.div>
        )}

        {currentPage === 'brief' && (
          <motion.div
            key="brief"
            variants={pageVariants}
            initial="initial"
            animate="enter"
            exit="exit"
          >
            <BriefInputPage
              onNext={handleBriefSubmit}
              onBack={() => setCurrentPage('style')}
            />
          </motion.div>
        )}

        {currentPage === 'loading' && (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <GenerationLoading />
          </motion.div>
        )}

        {currentPage === 'approval' && storyData.character && (
          <motion.div
            key="approval"
            variants={pageVariants}
            initial="initial"
            animate="enter"
            exit="exit"
          >
            <CharacterApproval
              character={storyData.character}
              onApprove={handleCharacterApprove}
              onRegenerate={handleCharacterRegenerate}
            />
          </motion.div>
        )}

        {currentPage === 'reading' && storyData.pages.length > 0 && (
          <motion.div
            key="reading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <StoryReader
              pages={storyData.pages}
              onHome={handleBackToLanding}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
