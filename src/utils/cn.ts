/**
 * Utility function to merge classnames (handles conditional classes)
 * Similar to clsx or classnames library
 */
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes
    .filter((cls): cls is string => Boolean(cls))
    .join(' ');
}
