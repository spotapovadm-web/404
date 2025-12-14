import { GenPriotity } from "../enums";

export type PriorityType = typeof GenPriotity[keyof typeof GenPriotity];