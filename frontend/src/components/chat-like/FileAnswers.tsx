import { Icon } from "@iconify-icon/react";
import {
  analyzeComplexity,
  generateTest,
  validate,
  validateBatch,
} from "@lib/api";
import type { TestType } from "@lib/types";
import { useEffect, useRef, useState } from "react";
import hljs from "highlight.js";
import { onCopy } from "@lib/callbacks";
import { ValidationPopup, WarningPopup } from "@/components";
import { RetryError } from "@lib/errors";

function FileAnswer({ files }: { files: Record<string, Array<File>> }) {
  const [execution_time, setExecutionTime] = useState(0);
  const [err, setErr] = useState(false);
  const [loading, setLoading] = useState(true);

  const [content, setMessageContent] = useState<Record<string, any>>({});
  const [warnsOpened, setWarnsOpened] = useState(false);

  const effectRan = useRef(false);

  useEffect(() => {
    if (effectRan.current) return;
    const start = performance.now();

    const func = async () => {
      try {
        for (const test_t of Object.keys(files)) {
          const test_type = test_t as TestType;
          let test_cases: Array<string> = [];

          for (const file of Array.from(files[test_type])) {
            const test_case = await file.text();
            test_cases = [...test_cases, test_case];
          }

          const type_content: Record<string, any> = {};

          const validation = (await validateBatch(test_type, test_cases)) as {
            detailed_results?: Array<Record<string, any>>;
          };
          const complexity = (await analyzeComplexity(test_cases)) as {
            detailed_analysis?: Array<Record<string, any>>;
          };

          if (validation?.detailed_results && files[test_t]) {
            Array.from(validation.detailed_results).forEach((obj, index) => {
              const filename = files[test_t][index].name;

              type_content[filename] = {
                warnings: [...obj?.warnings],
                compliance: { ...obj?.compliance },
              };
            });
          }

          if (complexity?.detailed_analysis && files[test_t]) {
            Array.from(complexity.detailed_analysis).forEach((obj, index) => {
              const filename = files[test_t][index].name;

              type_content[filename] = {
                ...(type_content[filename] ? type_content[filename] : {}),
                complexity_level: [...obj?.complexity_level],
              };
            });
          }

          setMessageContent((prev) => ({
            ...prev,
            [test_type]: type_content,
          }));
        }

        setExecutionTime((performance.now() - start) / 1000);
        setLoading(false);
      } catch (err) {
        if (err instanceof RetryError) {
          func();
          return;
        }

        setErr(true);
        console.log(err);
      }
    };

    func();

    effectRan.current = true;
  }, []);

  return (
    <div className="relative flex flex-col bg-primary/40 backdrop-blur-2xl rounded-2xl max-w-[85vw] ml-[3vw] p-5 transition-all duration-150">
      {err === false ? (
        loading === true ? (
          <Icon icon="eos-icons:bubble-loading" width={25} />
        ) : (
          <>
            <p>Думал на протяжении {execution_time.toFixed(2)} сек.</p>
            {Object.keys(content).map((key, index) => (
              <div key={index} className="flex flex-col">
                <span className="flex gap-1">
                  <p className="font-bold">Тип теста:</p>
                  <p>{key}</p>
                </span>
                {Object.keys(content[key]).map((fileKey, index) => (
                    <div key={index}>
                      <span className="flex gap-1">
                        <p className="font-bold">Файл:</p>
                        <p>{fileKey}</p>
                      </span>

                      {content[key][fileKey].complexity_level && (
                        <span className="flex gap-1">
                          <p className="font-bold">Уровень усложнёности:</p>
                          <p>{content[key][fileKey].complexity_level}</p>
                        </span>
                      )}

                      {content[key][fileKey].compliance && (
                        <p className="font-bold">Валидации:</p>
                      )}

                      {content[key][fileKey].compliance && Object.keys(content[key][fileKey].compliance).map((compKey, index) => (
                        <span key={index} className="flex gap-1">
                          <p>&#8226; {compKey}</p>
                          {content[key][fileKey].compliance[compKey] !== true ? (
                            <Icon
                              className="text-red-400"
                              icon="material-symbols:error-rounded"
                              width={20}
                            />
                          ) : (
                            <Icon className="text-green-400" icon="mdi:success" width={20} />
                          )}
                        </span>
                      ))}

                      {content[key][fileKey].warnings && (
                        <p className="font-bold">Предупреждения: </p>
                      )}

                      {content[key][fileKey].warnings && Array.from(content[key][fileKey].warnings).map((warns, index) => (
                        <p key={index}>&#8226; {warns as string}</p>
                      ))}

                    </div>
                ))}
              </div>
            ))}
          </>
        )
      ) : (
        <span className="flex gap-1">
          <Icon
            icon="material-symbols:error-rounded"
            width={20}
            className="text-red-400"
          />
          <p>Ошибка! Проверьте консоль разработчика.</p>
        </span>
      )}
    </div>
  );
}

export default FileAnswer;
