export type JobStatus = 'queued' | 'processing' | 'completed' | 'failed';
export type IflowMatchStatus = 'not_started' | 'processing' | 'completed' | 'failed' | 'unknown';

export interface FileInfo {
  xml_files: number;
  properties_files: number;
  json_files: number;
  yaml_files: number;
  raml_files: number;
  dwl_files: number;
  other_files: number;
  total_files: number;
}

export interface ParsedDetails {
  flows: number;
  subflows: number;
  configs: number;
  error_handlers: number;
}

export interface JobFiles {
  markdown: string;
  html: string;
  visualization: string;
}

export interface IflowMatchFiles {
  report: string;
  summary: string;
}

export interface JobInfo {
  id: string;
  status: JobStatus;
  created: string;
  last_updated: string;
  enhance: boolean;
  files: JobFiles | null;
  processing_step: string | null;
  processing_message: string | null;
  file_info: FileInfo | null;
  parsed_details: ParsedDetails | null;
  error: string | null;

  // iFlow match fields
  iflow_match_status?: IflowMatchStatus;
  iflow_match_message?: string;
  iflow_match_files?: IflowMatchFiles;
  iflow_match_result?: {
    message: string;
    [key: string]: any;
  };
}