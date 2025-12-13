import type { RefObject } from "react";
import type { TestType } from "../types";
import toast from "react-hot-toast";
import { Answer } from "@/components";

const onSendButton = (req: RefObject<HTMLInputElement | null>, test_t: RefObject<HTMLSelectElement | null>, product: RefObject<HTMLInputElement | null>, addAnswer: CallableFunction) => {
    const product_name = product.current?.value;
    if (!product_name || product_name.length === 0) {
        return toast.error("Введите имя продукта")
    }

    const requirement = req.current?.value;
    if (!requirement || requirement.length === 0) {
        return toast.error("Введите требование тест кейса")
    }
    const test_type = test_t.current?.value as TestType;
    
    addAnswer(<Answer product_name={product_name} req={requirement} test_type={test_type} />)
}

export { onSendButton }