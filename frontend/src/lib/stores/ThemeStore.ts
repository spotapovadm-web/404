import { create } from "zustand";
import { Theme } from "@lib/enums/";
import type { ThemeType } from "@lib/types";

const useThemeStore = create<{ theme: ThemeType; toggleTheme: () => void }>((set, get) => ({
    theme: Theme.WHITE,
    toggleTheme: () => 
        set({
            theme: get().theme === Theme.WHITE ? Theme.DARK : Theme.WHITE
        })
}));

export default useThemeStore;