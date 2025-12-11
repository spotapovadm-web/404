import type { TestType, PriorityType } from "../types";

const API_BASE_PATH = 'http://localhost:8000/api/v1';

const generateTest = async (requirement: string, test_type: TestType, product: string, priority: PriorityType): Promise<Record<string, any>> => {
    const res = await fetch(API_BASE_PATH + '/generate', {
        method: 'POST',
        body: JSON.stringify({
            requirement: requirement,
            test_type: test_type,
            product: product,
            priority: priority
        })
    });

    if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

    return Promise.resolve(await res.json());
};

const generateTestBatch = async (requirements: Array<string>, test_type: TestType, product: string): Promise<Record<string, any>> => {
    const res = await fetch(API_BASE_PATH + '/generate-batch', {
        method: 'POST',
        body: JSON.stringify({
            requirements: requirements,
            test_type: test_type,
            product: product
        })
    });

    if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

    return Promise.resolve(await res.json());
};

const generateTestFromOpenAPI = async (spec_url: string): Promise<Record<string, any>> => {
    const res = await fetch(API_BASE_PATH + '/generate-from-openapi', {
        method: 'POST',
        body: JSON.stringify({
            spec_url: spec_url
        })
    });

    if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

    return Promise.resolve(await res.json());
};

const getExamples = async (): Promise<Record<string, any>> => {
    const res = await fetch(API_BASE_PATH + '/examples', {
        method: 'GET'
    });

    if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

    return Promise.resolve(await res.json());
};

const getConnectionStatus = async (): Promise<Record<string, any>> => {
    const res = await fetch(API_BASE_PATH + '/status', {
        method: 'GET'
    });

    if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

    return Promise.resolve(await res.json());
};

const getFormats = async (): Promise<Record<string, any>> => {
    const res = await fetch(API_BASE_PATH + '/formats', {
        method: 'GET'
    });

    if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

    return Promise.resolve(await res.json());
};


const optimizeGen = async (test_cases: string, analyze_coverage: boolean, find_duplicates: boolean): Promise<Record<string, any>> => {
    const res = await fetch(API_BASE_PATH + '/optimize', {
        method: 'POST',
        body: JSON.stringify({
            test_cases: test_cases,
            analyze_coverage: analyze_coverage,
            find_duplicates: find_duplicates
        })
    });

    if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

    return Promise.resolve(await res.json());
};

const removeDuplicates = async (keep_first: boolean = true): Promise<Record<string, any>> => {
    const res = await fetch(API_BASE_PATH + '/remove-duplicates', {
        method: 'POST',
        body: JSON.stringify({
            keep_first: keep_first
        })
    });

    if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

    return Promise.resolve(await res.json());
}

const analyzeComplexity = async (): Promise<Record<string, any>> => {
    const res = await fetch(API_BASE_PATH + '/analyze-complexity', {
        method: 'POST'
    });

    if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

    return Promise.resolve(await res.json());
}

const validate = async (test_case: string, test_type: TestType): Promise<Record<string, any>> => {
    const res = await fetch(API_BASE_PATH + '/validate', {
        method: 'POST',
        body: JSON.stringify({
            test_case: test_case,
            test_type: test_type
        })
    });

    if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

    return Promise.resolve(await res.json());
}

const validateBatch = async (test_type: TestType): Promise<Record<string, any>> => {
    const res = await fetch(API_BASE_PATH + '/validate-batch', {
        method: 'POST',
        body: JSON.stringify({
            test_type: test_type
        })
    });

    if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

    return Promise.resolve(await res.json());
}

const checkStandarts = async (test_case: string): Promise<Record<string, any>> => {
    const res = await fetch(API_BASE_PATH + '/validate-batch', {
        method: 'POST',
        body: JSON.stringify({
            test_case: test_case
        })
    });

    if (!res.ok) throw new Error(`HTTP Error! Status: ${res.status}`);

    return Promise.resolve(await res.json());
}

export { generateTest, generateTestBatch, generateTestFromOpenAPI,
    getExamples, getConnectionStatus, getFormats, optimizeGen,
    removeDuplicates, analyzeComplexity, validate, validateBatch, checkStandarts };