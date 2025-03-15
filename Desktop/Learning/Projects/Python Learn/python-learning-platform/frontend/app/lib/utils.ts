import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * A utility function for conditionally joining CSS class names together
 * Uses clsx and tailwind-merge to handle class names properly
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
} 