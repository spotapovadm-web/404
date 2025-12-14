import { GenTestType } from '../enums';

export type TestType = typeof GenTestType[keyof typeof GenTestType];
