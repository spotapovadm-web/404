import type { MouseEventHandler, ReactNode } from "react";
import { forwardRef } from "react";

type ButtonProps = {
  onClick?: MouseEventHandler<HTMLButtonElement>;
  children?: ReactNode;
  className?: string;
};

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ onClick, children, className = "" }, ref) => (
    <button
      ref={ref} // attach the ref here
      onClick={onClick}
      className={`p-[1vh] bg-accent rounded-3xl flex items-center justify-center cursor-pointer ${className}`}
    >
      {children}
    </button>
  )
);

Button.displayName = "Button";

export default Button;
