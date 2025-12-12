import { useEffect, useState } from "react";
import type { RefObject } from "react";
import { generateTest } from '@lib/api'

const onSendButton = async (input: RefObject<HTMLInputElement>, test_t: RefObject<HTMLSelectElement>) => {
    const requirement = input.current?.value;
    const test_type = test_t.current?.value;

    const value = await generateTest(requirement, test_type,)
}

export { onSendButton }