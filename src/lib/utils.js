import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

// Combine Tailwind + clsx classes safely
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
