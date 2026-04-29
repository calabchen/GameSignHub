"""库洛论坛每日任务.

执行流程:
  1. 获取任务列表 (/encourage/level/getTaskProcess)
  2. 论坛签到 (/user/signIn)
  3. 浏览帖子 (/forum/list → /forum/getPostDetail × 3)
  4. 点赞帖子 (/forum/list → /forum/like × 5)
  5. 分享帖子 (/encourage/level/shareTask)
"""

import asyncio
import random

from plugins.kuro_plugin.client import KuroApiError, KuroHttpClient


class KuroForumTasks:
    """库洛社区论坛每日任务."""

    def __init__(self, client: KuroHttpClient) -> None:
        self.client = client

    async def execute_all(self) -> list[dict]:
        """执行所有论坛任务.

        Returns:
            [{"status": "success"|"failed"|"skipped", "task": "...", "message": "..."}]
        """
        results: list[dict] = []

        # 获取任务列表
        try:
            task_data = await self._get_task_list()
        except KuroApiError as e:
            return [{"status": "failed", "task": "获取任务列表", "message": str(e)}]

        task_items = task_data.get("data", {}).get("taskList", [])
        if not task_items:
            task_items = task_data.get("data", {}).get("dailyTask", [])

        for task in task_items:
            remark = task.get("remark", "")
            process = task.get("process", 0)

            if process == 1:
                results.append({"status": "skipped", "task": remark, "message": "已完成"})
                continue

            try:
                if remark == "用户签到":
                    r = await self._forum_sign_in()
                elif "浏览" in remark:
                    r = await self._browse_posts()
                elif "点赞" in remark:
                    r = await self._like_posts()
                elif "分享" in remark:
                    r = await self._share_post()
                else:
                    r = {"status": "skipped", "task": remark, "message": "未知任务"}
            except KuroApiError as e:
                r = {"status": "failed", "task": remark, "message": str(e)}
            except Exception as e:
                r = {"status": "failed", "task": remark, "message": repr(e)}

            r["task"] = remark
            results.append(r)
            await asyncio.sleep(random.uniform(0.5, 1.5))

        # 获取金币汇总
        gold = await self._get_total_gold()
        if gold:
            results.append({"status": "success", "task": "金币汇总", "message": gold})

        return results

    async def _get_task_list(self) -> dict:
        return await self.client.bbs_post("/encourage/level/getTaskProcess", {"gameId": "0"})

    async def _forum_sign_in(self) -> dict:
        resp = await self.client.bbs_post("/user/signIn", {"gameId": "2"})
        if resp.get("code") == 200:
            return {"status": "success", "message": resp.get("msg", "签到成功")}
        return {"status": "failed", "message": resp.get("msg", "签到失败")}

    async def _browse_posts(self) -> dict:
        posts = await self._get_feed_posts()
        count = 0
        for post in posts[:3]:
            try:
                await self.client.bbs_post("/forum/getPostDetail", {"postId": post["id"]})
                count += 1
                await asyncio.sleep(random.uniform(0.3, 0.8))
            except KuroApiError:
                pass
        return {"status": "success", "message": f"浏览 {count} 篇"}

    async def _like_posts(self) -> dict:
        posts = await self._get_feed_posts()
        count = 0
        for post in posts[:5]:
            try:
                await self.client.bbs_post("/forum/like", {
                    "postId": post["id"],
                    "isLike": "1",
                })
                count += 1
                await asyncio.sleep(random.uniform(0.3, 0.8))
            except KuroApiError:
                pass
        return {"status": "success", "message": f"点赞 {count} 次"}

    async def _share_post(self) -> dict:
        await self.client.bbs_post("/encourage/level/shareTask")
        return {"status": "success", "message": "分享完成"}

    async def _get_feed_posts(self) -> list[dict]:
        resp = await self.client.bbs_post("/forum/list")
        data = resp.get("data", {})
        return (
            data.get("postList", [])
            or data.get("feedList", [])
            or data.get("forumPostList", [])
            or data.get("list", [])
        )

    async def _get_total_gold(self) -> str:
        try:
            resp = await self.client.bbs_post("/encourage/gold/getTotalGold")
            if resp.get("code") == 200:
                return str(resp["data"].get("totalGold", ""))
        except KuroApiError:
            pass
        return ""
