import { useEffect, useState } from "react";
import type { RefObject } from "react";
import { generateTest } from '@lib/api'
import type { TestType } from "../types";
import toast from "react-hot-toast";
import { Answer } from "@/components";

const onSendButton = async (req: RefObject<HTMLInputElement | null>, test_t: RefObject<HTMLSelectElement | null>, product: RefObject<HTMLInputElement | null>, addAnswer: CallableFunction) => {
    const product_name = product.current?.value;
    if (!product_name || product_name.length === 0) {
        return toast.error("Введите имя продукта")
    }

    const requirement = req.current?.value;
    if (!requirement || requirement.length === 0) {
        return toast.error("Введите требование тест кейса")
    }
    const test_type = test_t.current?.value as TestType;
    
    addAnswer(<Answer />)

    const value = await generateTest(requirement, test_type, product_name, "NORMAL");
}

export { onSendButton }