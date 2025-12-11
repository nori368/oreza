/**
 * Scroll to Bottom Button
 * Floating button that appears when user scrolls up
 * Provides quick navigation to the latest messages
 */

import { useEffect, useState } from 'react';
import { ArrowDown } from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';

export function ScrollToBottomButton({ containerRef, threshold = 100 }) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const container = containerRef?.current || window;
    
    const handleScroll = () => {
      if (containerRef?.current) {
        // For scrollable container
        const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
        const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
        setIsVisible(distanceFromBottom > threshold);
      } else {
        // For window scroll
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight;
        const clientHeight = document.documentElement.clientHeight;
        const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
        setIsVisible(scrollTop > 100 && distanceFromBottom > threshold);
      }
    };

    if (containerRef?.current) {
      containerRef.current.addEventListener('scroll', handleScroll);
    } else {
      window.addEventListener('scroll', handleScroll);
    }

    // Initial check
    handleScroll();

    return () => {
      if (containerRef?.current) {
        containerRef.current.removeEventListener('scroll', handleScroll);
      } else {
        window.removeEventListener('scroll', handleScroll);
      }
    };
  }, [containerRef, threshold]);

  const scrollToBottom = () => {
    if (containerRef?.current) {
      containerRef.current.scrollTo({
        top: containerRef.current.scrollHeight,
        behavior: 'smooth'
      });
    } else {
      window.scrollTo({
        top: document.documentElement.scrollHeight,
        behavior: 'smooth'
      });
    }
  };

  if (!isVisible) return null;

  return (
    <Button
      onClick={scrollToBottom}
      className="fixed right-6 bottom-24 z-50 h-12 w-12 rounded-full shadow-lg transition-all hover:scale-110 active:scale-95"
      size="icon"
      variant="default"
      aria-label="Scroll to bottom"
    >
      <ArrowDown className="h-5 w-5" />
    </Button>
  );
}
