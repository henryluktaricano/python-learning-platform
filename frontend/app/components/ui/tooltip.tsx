'use client';

import * as React from 'react';
import { cn } from '@/app/lib/utils';

interface TooltipProviderProps {
  children: React.ReactNode;
  delayDuration?: number;
}

const TooltipProvider = ({
  children,
  delayDuration = 700,
}: TooltipProviderProps) => {
  return (
    <TooltipContext.Provider value={{ delayDuration }}>
      {children}
    </TooltipContext.Provider>
  );
};

interface TooltipContextValue {
  delayDuration: number;
}

const TooltipContext = React.createContext<TooltipContextValue>({
  delayDuration: 700,
});

const useTooltip = () => React.useContext(TooltipContext);

interface TooltipProps {
  children: React.ReactNode;
}

const Tooltip = ({ children }: TooltipProps) => {
  return <div className="relative inline-block">{children}</div>;
};

interface TooltipTriggerProps {
  children: React.ReactNode;
  asChild?: boolean;
}

const TooltipTrigger = React.forwardRef<HTMLButtonElement, TooltipTriggerProps & React.HTMLAttributes<HTMLButtonElement>>(
  ({ children, asChild = false, ...props }, ref) => {
    return (
      <button ref={ref} type="button" {...props}>
        {children}
      </button>
    );
  }
);
TooltipTrigger.displayName = 'TooltipTrigger';

interface TooltipContentProps {
  children: React.ReactNode;
  side?: 'top' | 'right' | 'bottom' | 'left';
  align?: 'start' | 'center' | 'end';
  className?: string;
}

const TooltipContent = React.forwardRef<HTMLDivElement, TooltipContentProps & React.HTMLAttributes<HTMLDivElement>>(
  ({ children, side = 'top', align = 'center', className, ...props }, ref) => {
    const [isVisible, setIsVisible] = React.useState(false);
    const { delayDuration } = useTooltip();

    React.useEffect(() => {
      const showTimer = setTimeout(() => setIsVisible(true), delayDuration);
      return () => clearTimeout(showTimer);
    }, [delayDuration]);

    if (!isVisible) return null;

    const sideClasses = {
      top: 'bottom-full mb-2',
      right: 'left-full ml-2',
      bottom: 'top-full mt-2',
      left: 'right-full mr-2',
    };

    const alignClasses = {
      start: 'origin-bottom-left left-0',
      center: 'origin-bottom transform -translate-x-1/2 left-1/2',
      end: 'origin-bottom-right right-0',
    };

    return (
      <div
        ref={ref}
        className={cn(
          'absolute z-50 px-3 py-1.5 text-xs bg-gray-900 text-white rounded-md shadow-md',
          sideClasses[side],
          alignClasses[align],
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);
TooltipContent.displayName = 'TooltipContent';

export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider }; 