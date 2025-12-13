import { Icon } from '@iconify-icon/react';
import { generateTest } from "@lib/api";
import type { TestType } from "@lib/types";
import { useEffect, useRef, useState } from "react";
import hljs from "highlight.js";

function Answer({ req, test_type, product_name }: { req: string, test_type: TestType, product_name: string}) {
    const [test_case, setTestCase] = useState<string>("");
    const [err, setErr] = useState(false);
    const [loading, setLoading] = useState(true);

    const effectRan = useRef(false);

    useEffect(() => {
        if (effectRan.current) return;
        const func = async () => {
            try {
                const value = await generateTest(req, test_type, product_name, "NORMAL");
                setTestCase(value?.test_case);
                setLoading(false);
            }
            catch (err) {
                setErr(true);
                console.log(err);
            }
        };

        func();

        effectRan.current = true;
    }, []);
    

    return (
        <div className="flex flex-col bg-primary rounded-2xl max-w-[95vw] p-5 transition-all duration-150">
            {err === false ? 
                (loading === true ? (
                    <Icon icon="eos-icons:bubble-loading" width={25}/>
                ) : (
                    <pre className="bg-black/40 rounded-2xl whitespace-pre overflow-x-scroll p-2 ">
                        <code 
                        className="font-code python"
                        dangerouslySetInnerHTML={{
                            __html: hljs.highlight(test_case, {language: "python"}).value
                        }}
                        />
                    </pre>
                )) : (
                    <span className='flex gap-1'>
                        <Icon icon='material-symbols:error-rounded' width={23} className='text-red-400'/>
                        <p>Ошибка! Проверьте консоль разработчика.</p>
                    </span>
                )
            }
            
        </div>
    );
}

export default Answer;