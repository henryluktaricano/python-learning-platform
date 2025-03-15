'use client';

import * as React from 'react';
import { cn } from '@/app/lib/utils';

interface DropdownMenuProps {
  children: React.ReactNode;
}

const DropdownMenu = ({ children }: DropdownMenuProps) => {
  return <div className="relative inline-block text-left">{children}</div>;
};

interface DropdownMenuTriggerProps {
  children: React.ReactNode;
  asChild?: boolean;
}

const DropdownMenuTrigger = ({ children, asChild = false }: DropdownMenuTriggerProps) => {
  const [open, setOpen] = React.useState(false);

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    setOpen(!open);
  };

  return (
    <>
      <div onClick={handleClick} className="inline-flex cursor-pointer">
        {children}
      </div>
      {open && (
        <div
          className="fixed inset-0 z-50"
          onClick={() => setOpen(false)}
        />
      )}
    </>
  );
};

interface DropdownMenuContentProps {
  children: React.ReactNode;
  align?: 'start' | 'center' | 'end';
  side?: 'top' | 'right' | 'bottom' | 'left';
  sideOffset?: number;
  className?: string;
}

const DropdownMenuContent = ({
  children,
  align = 'start',
  side = 'bottom',
  sideOffset = 4,
  className,
}: DropdownMenuContentProps) => {
  const alignClasses = {
    start: 'origin-top-left left-0',
    center: 'origin-top',
    end: 'origin-top-right right-0',
  };

  const sideClasses = {
    top: 'bottom-full mb-2',
    right: 'left-full ml-2',
    bottom: 'top-full mt-2',
    left: 'right-full mr-2',
  };

  return (
    <div
      className={cn(
        'absolute z-50 min-w-[8rem] overflow-hidden rounded-md border border-gray-200 bg-white p-1 shadow-md animate-in',
        alignClasses[align],
        sideClasses[side],
        className
      )}
      style={{ 
        marginTop: side === 'bottom' ? sideOffset : undefined,
        marginBottom: side === 'top' ? sideOffset : undefined,
        marginLeft: side === 'right' ? sideOffset : undefined,
        marginRight: side === 'left' ? sideOffset : undefined,
      }}
    >
      {children}
    </div>
  );
};

interface DropdownMenuItemProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  className?: string;
}

const DropdownMenuItem = React.forwardRef<HTMLButtonElement, DropdownMenuItemProps>(
  ({ className, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          'relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors focus:bg-gray-100 focus:text-gray-900 hover:bg-gray-100 data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
          className
        )}
        {...props}
      />
    );
  }
);
DropdownMenuItem.displayName = 'DropdownMenuItem';

export { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem }; 