import React, { forwardRef, type HTMLAttributes } from 'react';
import { type HandleProps, Handle } from '@xyflow/react';
import cn from 'classnames';

const flexDirections = {
  top: 'flex-col',
  right: 'flex-row-reverse justify-end',
  bottom: 'flex-col-reverse justify-end',
  left: 'flex-row',
};

export const LabeledHandle = forwardRef<
  HTMLDivElement,
  HandleProps &
    HTMLAttributes<HTMLDivElement> & {
      title: string;
      handleClassName?: string;
      labelClassName?: string;
    }
>(({ className, labelClassName, handleClassName, title, position, ...props }, ref) => (
  <div
    ref={ref}
    title={title}
    className={cn('relative flex items-center bg-slate-300 py-2', flexDirections[position], className)}
  >
    <Handle
      ref={ref}
      position={position}
      className={cn(
        'h-[11px] w-[11px] rounded-full !bg-red-500 border !border-red-300 transition dark:border-secondary dark:bg-secondary',
        handleClassName,
      )}
      {...props}
    />
    <label className={cn('ps-5 text-foreground', labelClassName)}>{title}</label>
  </div>
));

LabeledHandle.displayName = 'LabeledHandle';
