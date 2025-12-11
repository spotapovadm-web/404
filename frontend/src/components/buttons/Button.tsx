import type { MouseEventHandler, ReactNode } from 'react';

function Button({ onClick, children, className = '' }: { onClick?: MouseEventHandler<HTMLButtonElement>, children?: ReactNode, className?: string }) {
    return (
        <button onClick={onClick} className={`p-[1vh] bg-accent rounded-3xl flex items-center justify-center ${className}`}>
            {children}
        </button>
    );
}

export default Button;