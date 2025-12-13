import type { RefObject } from "react";
import type { TestType } from "../types";
import toast from "react-hot-toast";
import { Request, Answer } from "@/components";
import type { JSX } from "react";

const onSendButton = (reqObj: RefObject<HTMLInputElement | null>, testTypeObj: RefObject<HTMLSelectElement | null>, productObj: RefObject<HTMLInputElement | null>, addHistory: CallableFunction, chatHistory: JSX.Element[]) => {
    const product_name = productObj.current?.value;
    if (!product_name || product_name.length === 0) {
        return toast.error("Введите имя продукта")
    }

    const requirement = reqObj.current?.value;
    if (!requirement || requirement.length === 0) {
        return toast.error("Введите требование тест кейса")
    }
    const test_type = testTypeObj.current?.value as TestType;
    
    addHistory(<Request key={chatHistory.length} test_type={test_type} product_name={product_name} requirement={requirement} />)
    addHistory(<Answer key={chatHistory.length + 1} product_name={product_name} req={requirement} test_type={test_type} />)
    
    if (reqObj.current instanceof HTMLInputElement) {
        reqObj.current.value = '';
    }
}

const onCopy = (content: string) => {
    navigator.clipboard.writeText(content)
    .then(() => toast.success("Скопирован текст"))
    .catch(() => toast.error("Ошибка копирования"))
};

export { onSendButton, onCopy }