import type { ReactElement, RefObject } from "react";
import type { TestType } from "../types";
import toast from "react-hot-toast";
import { Request, Answer, FilesRequest, FileAnswer } from "@/components";
import type { JSX } from "react";

const onSendButton = (reqObj: RefObject<HTMLInputElement | null>, testTypeObj: RefObject<HTMLSelectElement | null>, productObj: RefObject<HTMLInputElement | null>, addHistory: CallableFunction, chatHistory: JSX.Element[]) => {
    const product_name = productObj.current?.value;
    if (!product_name || product_name.length === 0) {
        return toast.error("Введите название продукта")
    }

    const requirement = reqObj.current?.value;
    if (!requirement || requirement.length === 0) {
        return toast.error("Введите требование к тест кейсу")
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

const onTestFileChange = async (e: React.ChangeEvent<HTMLInputElement>, setFilesPopupOpen: CallableFunction, setFilesForPopup: CallableFunction) => {
    const files = e.target.files;
    if (!files) {
        return
    }
    
    if (Array.from(files).length == 0) {
        return
    }

    setFilesForPopup(Array.from(files));
    setFilesPopupOpen(true);

    e.target.value = '';

    // addHistory(<FilesRequest key={chatHistory.length} files={files} />)
}

const onDoBetterBatch = (test_types: Record<string, string>, files: FileList | null, addHistory: CallableFunction, chatHistory: Array<JSX.Element>) => {
    if (!files)
        return

    let sorted: Record<string, Array<File>> = {
        "UI": [],
        "E2E": [],
        "API": [],
        "UNIT": []
    }

    for (const file of Array.from(files)) {
        sorted[test_types[file.name]] = [...sorted[test_types[file.name]], file]
    }

    for (const key of Object.keys(sorted)) {
        if (sorted[key].length === 0 ) {
            delete sorted[key];
        }
    }

    addHistory(<FilesRequest key={chatHistory.length} files={sorted} />)
    addHistory(<FileAnswer key={chatHistory.length + 1} files={sorted} />)
} 

export { onSendButton, onCopy, onTestFileChange, onDoBetterBatch }