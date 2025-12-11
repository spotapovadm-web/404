import type { MouseEventHandler, ReactNode } from 'react';

function Button({ onClick, contents }: { onClick: MouseEventHandler<HTMLButtonElement>, contents: ReactNode }) {
    return (
        <button onClick={onClick}>
            {contents}
        </button>
    );
}

export default Button;