import type { TestType, PriorityType } from "../types";
import { RetryError } from "../errors";

const API_BASE_PATH = "http://localhost:8000/api/v1";

const generateTest = async (
  requirement: string,
  test_type: TestType,
  product: string,
  priority: PriorityType
): Promise<Record<string, any>> => {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), 30000);

  try {
    const res = await fetch(API_BASE_PATH + `/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        requirement: requirement,
        test_type: test_type,
        product: product,
        priority: priority,
      }),
      signal: controller.signal,
    });

    if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

    return Promise.resolve(await res.json());
  } catch (e) {
    if (e instanceof DOMException && e.name === "AbortError") {
      throw new RetryError(
        "Retry the request, maybe this time agent will reply."
      );
    }
    console.log(e);
    throw e;
  } finally {
    clearTimeout(id);
  }
};

const generateTestBatch = async (
  requirements: Array<string>,
  test_type: TestType,
  product: string
): Promise<Record<string, any>> => {
  const res = await fetch(API_BASE_PATH + "/generate-batch", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      requirements: requirements,
      test_type: test_type,
      product: product,
    }),
  });

  if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

  return Promise.resolve(await res.json());
};

const generateTestFromOpenAPI = async (
  spec_url: string
): Promise<Record<string, any>> => {
  const res = await fetch(
    API_BASE_PATH + `/generate-from-openapi?spec_url=${spec_url}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

  return Promise.resolve(await res.json());
};

const getExamples = async (): Promise<Record<string, any>> => {
  const res = await fetch(API_BASE_PATH + "/examples", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

  return Promise.resolve(await res.json());
};

const getConnectionStatus = async (): Promise<Record<string, any>> => {
  const res = await fetch(API_BASE_PATH + "/status", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

  return Promise.resolve(await res.json());
};

const getFormats = async (): Promise<Record<string, any>> => {
  const res = await fetch(API_BASE_PATH + "/formats", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

  return Promise.resolve(await res.json());
};

const optimizeGen = async (
  test_cases: string,
  analyze_coverage: boolean,
  find_duplicates: boolean
): Promise<Record<string, any>> => {
  const res = await fetch(API_BASE_PATH + "/optimize", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      test_cases: test_cases,
      analyze_coverage: analyze_coverage,
      find_duplicates: find_duplicates,
    }),
  });

  if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

  return Promise.resolve(await res.json());
};

const removeDuplicates = async (
  requirements: Array<string>,
  keep_first: boolean = true
): Promise<Record<string, any>> => {
  const res = await fetch(
    API_BASE_PATH + `/remove-duplicates?keep_first=${keep_first}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify([...requirements]),
    }
  );

  if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

  return Promise.resolve(await res.json());
};

const analyzeComplexity = async (
  test_cases: Array<string>
): Promise<Record<string, any>> => {
  const res = await fetch(API_BASE_PATH + "/analyze-complexity", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify([...test_cases]),
  });

  if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

  return Promise.resolve(await res.json());
};

const validate = async (
  test_case: string,
  test_type: TestType
): Promise<Record<string, any>> => {
  const res = await fetch(API_BASE_PATH + "/validate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      test_case: test_case,
      test_type: test_type,
    }),
  });

  if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

  return Promise.resolve(await res.json());
};

const validateBatch = async (
  test_type: TestType,
  requirements: Array<string>
): Promise<Record<string, any>> => {
  const res = await fetch(
    API_BASE_PATH + `/validate-batch?test_type=${test_type}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify([...requirements]),
    }
  );

  if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

  return Promise.resolve(await res.json());
};

const checkStandarts = async (
  test_case: string
): Promise<Record<string, any>> => {
  const res = await fetch(API_BASE_PATH + "/check-standards", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      test_case: test_case,
    }),
  });

  if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

  return Promise.resolve(await res.json());
};

export {
  generateTest,
  generateTestBatch,
  generateTestFromOpenAPI,
  getExamples,
  getConnectionStatus,
  getFormats,
  optimizeGen,
  removeDuplicates,
  analyzeComplexity,
  validate,
  validateBatch,
  checkStandarts,
};
