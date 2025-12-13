import { Icon } from "@iconify-icon/react";
import { generateTest, validate } from "@lib/api";
import type { TestType } from "@lib/types";
import { useEffect, useRef, useState } from "react";
import hljs from "highlight.js";
import { onCopy } from "@lib/callbacks";
import ValidationPopup from "@components/popups/ValidationPopup";

function Answer({
  req,
  test_type,
  product_name,
}: {
  req: string;
  test_type: TestType;
  product_name: string;
}) {
  const [test_case, setTestCase] = useState("");
  const [execution_time, setExecutionTime] = useState(0);
  const [err, setErr] = useState(false);
  const [loading, setLoading] = useState(true);

  const [validsOpened, setOpenValids] = useState(false);
  const [validsLoading, setValidsLoading] = useState(true);
  const [validsErr, setValidsErr] = useState(false);
  const [validsCount, setValidsCount] = useState(0);
  const [validValidsCount, setValidValidsCount] = useState(0);
  const [validsRes, setValidsRes] = useState<Record<any, string>>({});

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

  const isFirstRun = useRef(true);
  useEffect(() => {
    if (isFirstRun.current) {
      isFirstRun.current = false;
      return;
    }

    const asyncFetch = async () => {
      try {
        const res = (await validate(test_case, test_type)) as Record<
          string,
          any
        >;
        setValidsCount(Object.values(res?.compliance).length);
        setValidValidsCount(
          Object.values(res?.compliance).filter((v) => v === true).length
        );
        setValidsRes(res);
        setValidsLoading(false);
      } catch (err) {
        console.log(err);
        setValidsErr(true);
      }
    };

    asyncFetch();
  }, [test_case]);

  return (
    <div className="relative flex flex-col bg-primary rounded-2xl max-w-[85vw] ml-[3vw] p-5 transition-all duration-150">
      {err === false ? (
        loading === true ? (
          <Icon icon="eos-icons:bubble-loading" width={25} />
        ) : (
          <>
            <div className="flex mb-4">
              <button
                onClick={() => {
                  if (!validsErr && !validsLoading) setOpenValids(!validsOpened);
                }}
                className="bg-black/10 rounded-2xl self-start p-2 flex gap-1 items-center"
              >
                <p>Валидации</p>
                {validsErr && (
                  <Icon
                    icon="material-symbols:error-rounded"
                    className="text-red-300"
                    width={20}
                  />
                )}
                {!validsErr && validsLoading && (
                  <Icon icon="eos-icons:bubble-loading" />
                )}
                {!validsErr &&
                  !validsLoading &&
                  validValidsCount + "/" + validsCount}
              </button>
              <ValidationPopup
                opened={validsOpened}
                validations={validsRes}
                onClose={() => setOpenValids(false)}
              />
            </div>

            <p>Думал на протяжении {execution_time} сек.</p>
            <button
              type="button"
              onClick={() => onCopy(test_case)}
              className="flex backdrop-blur-2xl items-center mt-24 gap-1 absolute z-10 border border-black/20 bg-black/20 self-end hover:border-white/40 active:bg-white/50 transition-colors duration-100 rounded-bl-2xl rounded-tr-2xl p-2"
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
            width={20}
            className="text-red-400"
          />
          <p>Ошибка! Проверьте консоль разработчика.</p>
        </span>
      )}
    </div>
  );
}

export default Answer;
