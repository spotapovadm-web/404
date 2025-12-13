import { Icon } from "@iconify-icon/react";
import { generateTest } from "@lib/api";
import type { TestType } from "@lib/types";
import { useEffect, useRef, useState } from "react";
import hljs from "highlight.js";
import { onCopy } from "@lib/callbacks";

function Answer({
  req,
  test_type,
  product_name
}: {
  req: string;
  test_type: TestType;
  product_name: string;
}) {
  const [test_case, setTestCase] = useState("");
  const [execution_time, setExecutionTime] = useState(0);
  const [err, setErr] = useState(false);
  const [loading, setLoading] = useState(true);

  const effectRan = useRef(false);

  useEffect(() => {
    if (effectRan.current) return;
    const func = async () => {
      try {
        const value = await generateTest(
          req,
          test_type,
          product_name,
          "NORMAL"
        );
        setTestCase(value?.test_case);
        setExecutionTime(value?.execution_time);


        setLoading(false);
      } catch (err) {
        setErr(true);
        console.log(err);
      }
    };

    func();

    effectRan.current = true;
  }, []);

  return (
    <div className="relative flex flex-col bg-primary rounded-2xl max-w-[85vw] ml-[3vw] p-5 transition-all duration-150">
      {err === false ? (
        loading === true ? (
          <Icon icon="eos-icons:bubble-loading" width={25} />
        ) : (
          <>
            <p>Думал на протяжении {execution_time} сек.</p>
            <button
              type="button"
              onClick={() => onCopy(test_case)}
              className="flex backdrop-blur-2xl items-center mt-10 gap-1 absolute z-10 border border-black/20 bg-black/20 self-end hover:border-white/40 active:bg-white/50 transition-colors duration-100 rounded-tr-2xl p-2"
            >
              <Icon icon="mingcute:copy-line" />
              <p>Копировать код</p>
            </button>
            <pre className="bg-black/40 rounded-2xl mt-4 whitespace-pre overflow-x-scroll p-2">
              <code
                className="font-code python"
                dangerouslySetInnerHTML={{
                  __html: hljs.highlight(test_case, { language: "python" })
                    .value,
                }}
              />
            </pre>
          </>
        )
      ) : (
        <span className="flex gap-1">
          <Icon
            icon="material-symbols:error-rounded"
            width={23}
            className="text-red-400"
          />
          <p>Ошибка! Проверьте консоль разработчика.</p>
        </span>
      )}
    </div>
  );
}

export default Answer;
